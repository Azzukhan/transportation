import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  Empty,
  Form,
  Input,
  Row,
  Select,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
} from "antd";
import type { ColumnsType } from "antd/es/table";

import {
  createInvoice,
  downloadInvoicePdf,
  listInvoices,
  markInvoicePaid,
} from "../api/invoices";
import { useCompanies } from "../hooks";
import type { InvoiceApi, InvoiceCreateInput } from "../types";
import { toast } from "../utils";

const { Title } = Typography;

const money = (value: string): string =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(Number(value));

export const UnpaidCompaniesRoute = () => {
  const [rows, setRows] = useState<InvoiceApi[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [form] = Form.useForm<InvoiceCreateInput>();
  const { companies } = useCompanies();

  const companyMap = useMemo(
    () => new Map(companies.map((company) => [company.id, company.name])),
    [companies],
  );

  const fetchRows = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const [unpaid, overdue] = await Promise.all([listInvoices("unpaid"), listInvoices("overdue")]);
      const merged = [...overdue, ...unpaid.filter((item) => item.status !== "overdue")];
      setRows(merged);
    } catch {
      setError("Failed to load unpaid invoices.");
      toast.error("Failed to load unpaid invoices.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void fetchRows();
  }, []);

  const onGenerate = async (values: InvoiceCreateInput): Promise<void> => {
    setIsSaving(true);
    try {
      await createInvoice(values);
      toast.success("Invoice generated successfully.");
      form.resetFields();
      await fetchRows();
    } catch {
      toast.error("Failed to generate invoice. Ensure unpaid trips exist for selected dates.");
    } finally {
      setIsSaving(false);
    }
  };

  const onMarkPaid = async (invoiceId: number): Promise<void> => {
    try {
      await markInvoicePaid(invoiceId);
      toast.success("Invoice marked as paid.");
      await fetchRows();
    } catch {
      toast.error("Failed to mark invoice as paid.");
    }
  };

  const onDownload = async (invoiceId: number, templateKey: string): Promise<void> => {
    try {
      const blob = await downloadInvoicePdf(invoiceId, templateKey);
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `invoice_${invoiceId}.pdf`;
      anchor.click();
      window.URL.revokeObjectURL(url);
    } catch {
      toast.error("Failed to download invoice PDF.");
    }
  };

  const columns: ColumnsType<InvoiceApi> = [
    {
      title: "Invoice",
      dataIndex: "id",
      render: (value: number) => `TAX/IN/${value}`,
    },
    {
      title: "Company",
      dataIndex: "company_id",
      render: (companyId: number) => companyMap.get(companyId) ?? `Company #${companyId}`,
    },
    {
      title: "Amount",
      dataIndex: "total_amount",
      render: (value: string) => money(value),
    },
    {
      title: "Due Date",
      dataIndex: "due_date",
      render: (value: string) => value,
    },
    {
      title: "Status",
      dataIndex: "status",
      render: (value: string) => <Tag color={value === "overdue" ? "red" : "gold"}>{value}</Tag>,
    },
    {
      title: "Action",
      key: "action",
      render: (_, record) => (
        <Space>
          <Button type="link" onClick={() => void onMarkPaid(record.id)}>
            Mark Paid
          </Button>
          <Button type="link" onClick={() => void onDownload(record.id, record.format_key)}>
            Download PDF
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="admin-page admin-fade">
      <div className="admin-page-head">
        <Title level={3}>Unpaid Invoices</Title>
      </div>

      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <Card>
          <Form<InvoiceCreateInput> form={form} layout="vertical" onFinish={(values) => void onGenerate(values)}>
            <Row gutter={12} className="admin-grid-gap">
              <Col xs={24} md={8}>
                <Form.Item label="Company" name="companyId" rules={[{ required: true }]}>
                  <Select size="large" options={companies.map((company) => ({ label: company.name, value: company.id }))} />
                </Form.Item>
              </Col>
              <Col xs={24} md={8}>
                <Form.Item label="From Date" name="startDate" rules={[{ required: true }]}>
                  <Input size="large" type="date" />
                </Form.Item>
              </Col>
              <Col xs={24} md={8}>
                <Form.Item label="To Date" name="endDate" rules={[{ required: true }]}>
                  <Input size="large" type="date" />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={12} className="admin-grid-gap">
              <Col xs={24} md={8}>
                <Form.Item label="Due Date" name="dueDate" rules={[{ required: true }]}>
                  <Input size="large" type="date" />
                </Form.Item>
              </Col>
              <Col xs={24} md={8}>
                <Form.Item label="Invoice Format" name="formatKey" initialValue="template_a" rules={[{ required: true }]}>
                  <Select
                    size="large"
                    options={[
                      { label: "Template A", value: "template_a" },
                      { label: "Template B", value: "template_b" },
                    ]}
                  />
                </Form.Item>
              </Col>
              <Col xs={24} md={8} style={{ display: "flex", alignItems: "end" }}>
                <Button type="primary" htmlType="submit" loading={isSaving} size="large">
                  Generate Invoice
                </Button>
              </Col>
            </Row>
          </Form>
        </Card>

        {error ? <Alert type="error" message={error} showIcon /> : null}

        <Card>
          {isLoading ? (
            <Spin />
          ) : rows.length === 0 ? (
            <Empty description="No unpaid invoices yet" />
          ) : (
            <Table rowKey="id" columns={columns} dataSource={rows} />
          )}
        </Card>
      </Space>
    </div>
  );
};
