import { useEffect, useMemo, useState } from "react";
import { Alert, Button, Card, Empty, Space, Spin, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

import { downloadInvoicePdf, listInvoices } from "../api/invoices";
import { useCompanies } from "../hooks";
import type { InvoiceApi } from "../types";
import { toast } from "../utils";

const { Title } = Typography;

const money = (value: string): string =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(Number(value));

export const PaidCompaniesRoute = () => {
  const [rows, setRows] = useState<InvoiceApi[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { companies } = useCompanies();

  const companyMap = useMemo(
    () => new Map(companies.map((company) => [company.id, company.name])),
    [companies],
  );

  const fetchRows = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      setRows(await listInvoices("paid"));
    } catch {
      setError("Failed to load paid invoices.");
      toast.error("Failed to load paid invoices.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void fetchRows();
  }, []);

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
      title: "Format",
      dataIndex: "format_key",
      render: (value: string) => <Tag>{value}</Tag>,
    },
    { title: "Generated", dataIndex: "generated_at", render: (value: string) => value.slice(0, 10) },
    { title: "Paid At", dataIndex: "paid_at", render: (value: string | null) => value?.slice(0, 10) ?? "-" },
    {
      title: "Action",
      key: "action",
      render: (_, record) => (
        <Button type="link" onClick={() => void onDownload(record.id, record.format_key)}>
          Download PDF
        </Button>
      ),
    },
  ];

  return (
    <div className="admin-page admin-fade">
      <div className="admin-page-head">
        <Title level={3}>Paid Invoices</Title>
      </div>

      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <Button onClick={() => void fetchRows()}>Refresh</Button>
        </div>

        {error ? <Alert type="error" message={error} showIcon /> : null}

        <Card>
          {isLoading ? (
            <Spin />
          ) : rows.length === 0 ? (
            <Empty description="No paid invoices yet" />
          ) : (
            <Table rowKey="id" columns={columns} dataSource={rows} />
          )}
        </Card>
      </Space>
    </div>
  );
};
