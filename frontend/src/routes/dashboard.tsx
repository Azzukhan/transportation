import { useEffect, useMemo, useState } from "react";
import {
  BankOutlined,
  DollarCircleOutlined,
  FileSearchOutlined,
  RiseOutlined,
} from "@ant-design/icons";
import { Alert, Card, Col, Empty, Row, Space, Spin, Statistic, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

import { listContactRequests, listQuoteRequests } from "../api/public";
import { useCompanies } from "../hooks";
import type { Company, ContactRequestApi, QuoteRequestApi } from "../types";

const { Title } = Typography;

const money = (value: number): string =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);

const companyColumns: ColumnsType<Company> = [
  { title: "Company", dataIndex: "name", key: "name" },
  { title: "Contact", dataIndex: "contactPerson", key: "contactPerson" },
  { title: "Email", dataIndex: "email", key: "email" },
  { title: "Phone", dataIndex: "phone", key: "phone" },
  { title: "Paid", dataIndex: "paidAmount", key: "paidAmount", render: (value: number) => money(value) },
  { title: "Unpaid", dataIndex: "unpaidAmount", key: "unpaidAmount", render: (value: number) => money(value) },
];

const contactColumns: ColumnsType<ContactRequestApi> = [
  { title: "Name", dataIndex: "name" },
  { title: "Phone", dataIndex: "phone" },
  { title: "Subject", dataIndex: "subject" },
  { title: "Status", dataIndex: "status" },
  { title: "Created", dataIndex: "created_at", render: (value: string) => value.slice(0, 10) },
];

const quoteColumns: ColumnsType<QuoteRequestApi> = [
  { title: "Name", dataIndex: "name" },
  { title: "Mobile", dataIndex: "mobile" },
  { title: "Freight", dataIndex: "freight" },
  { title: "Route", key: "route", render: (_, row) => `${row.origin} -> ${row.destination}` },
  { title: "Status", dataIndex: "status" },
  { title: "Created", dataIndex: "created_at", render: (value: string) => value.slice(0, 10) },
];

export const DashboardRoute = () => {
  const { companies, summary, isLoading, error } = useCompanies();
  const [contactRows, setContactRows] = useState<ContactRequestApi[]>([]);
  const [quoteRows, setQuoteRows] = useState<QuoteRequestApi[]>([]);
  const [isRequestLoading, setIsRequestLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadRequests = async (): Promise<void> => {
      setIsRequestLoading(true);
      try {
        const [contacts, quotes] = await Promise.all([listContactRequests(), listQuoteRequests()]);
        setContactRows(contacts);
        setQuoteRows(quotes);
      } finally {
        setIsRequestLoading(false);
      }
    };

    void loadRequests();
  }, []);

  const totalRequests = useMemo(
    () => contactRows.length + quoteRows.length,
    [contactRows.length, quoteRows.length],
  );

  return (
    <div className="admin-page admin-fade">
      <div className="admin-page-head">
        <Title level={2}>Dashboard Overview</Title>
      </div>

      <Space direction="vertical" size={14} style={{ width: "100%" }}>
        {error ? <Alert type="error" message={error} showIcon /> : null}

        <Row gutter={12} className="admin-grid-gap">
          <Col xs={24} md={12} xl={6}>
            <Card bordered={false}>
              <Statistic title="Total Companies" prefix={<BankOutlined />} value={summary.totalCompanies} />
            </Card>
          </Col>
          <Col xs={24} md={12} xl={6}>
            <Card bordered={false}>
              <Statistic title="Total Paid" prefix={<RiseOutlined />} value={money(summary.totalPaidAmount)} />
            </Card>
          </Col>
          <Col xs={24} md={12} xl={6}>
            <Card bordered={false}>
              <Statistic title="Total Unpaid" prefix={<DollarCircleOutlined />} value={money(summary.totalUnpaidAmount)} />
            </Card>
          </Col>
          <Col xs={24} md={12} xl={6}>
            <Card bordered={false}>
              <Statistic title="Public Requests" prefix={<FileSearchOutlined />} value={totalRequests} />
            </Card>
          </Col>
        </Row>

        <Card title="Companies">
          {isLoading ? (
            <Spin />
          ) : companies.length === 0 ? (
            <Empty description="No companies yet" />
          ) : (
            <Table rowKey="id" columns={companyColumns} dataSource={companies} pagination={{ pageSize: 8 }} />
          )}
        </Card>

        <Card title="Recent Contact Requests">
          {isRequestLoading ? (
            <Spin />
          ) : contactRows.length === 0 ? (
            <Empty description="No contact requests yet" />
          ) : (
            <Table rowKey="id" columns={contactColumns} dataSource={contactRows.slice(0, 6)} pagination={false} />
          )}
        </Card>

        <Card title="Recent Quote Requests">
          {isRequestLoading ? (
            <Spin />
          ) : quoteRows.length === 0 ? (
            <Empty description="No quote requests yet" />
          ) : (
            <Table rowKey="id" columns={quoteColumns} dataSource={quoteRows.slice(0, 6)} pagination={false} />
          )}
        </Card>
      </Space>
    </div>
  );
};
