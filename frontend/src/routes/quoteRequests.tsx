import { useEffect, useState } from "react";
import { Button, Card, Empty, Select, Space, Spin, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

import { listQuoteRequests, updateQuoteRequestStatus } from "../api/public";
import type { QuoteRequestApi } from "../types";
import { toast } from "../utils";

const { Title } = Typography;

const statusOptions = ["new", "in_progress", "quoted", "closed"];

export const QuoteRequestsRoute = () => {
  const [rows, setRows] = useState<QuoteRequestApi[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const load = async (): Promise<void> => {
    setIsLoading(true);
    try {
      setRows(await listQuoteRequests());
    } catch {
      toast.error("Failed to load quote requests.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const onStatusChange = async (requestId: number, status: string): Promise<void> => {
    try {
      const updated = await updateQuoteRequestStatus(requestId, status);
      setRows((current) => current.map((item) => (item.id === requestId ? updated : item)));
      toast.success("Quote request updated.");
    } catch {
      toast.error("Failed to update quote request.");
    }
  };

  const columns: ColumnsType<QuoteRequestApi> = [
    { title: "Name", dataIndex: "name" },
    { title: "Email", dataIndex: "email" },
    { title: "Mobile", dataIndex: "mobile" },
    { title: "Freight", dataIndex: "freight" },
    {
      title: "Route",
      key: "route",
      render: (_, row) => `${row.origin} -> ${row.destination}`,
    },
    { title: "Note", dataIndex: "note", ellipsis: true },
    {
      title: "Status",
      key: "status",
      render: (_, record) => (
        <Select
          value={record.status}
          style={{ width: 150 }}
          options={statusOptions.map((value) => ({ label: value, value }))}
          onChange={(value) => void onStatusChange(record.id, value)}
        />
      ),
    },
    {
      title: "Created",
      dataIndex: "created_at",
      render: (value: string) => value.slice(0, 10),
    },
  ];

  return (
    <div className="admin-page admin-fade">
      <div className="admin-page-head">
        <Title level={3}>Quote Requests</Title>
      </div>

      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <Button onClick={() => void load()}>Refresh</Button>
        </div>

        <Card>
          {isLoading ? (
            <Spin />
          ) : rows.length === 0 ? (
            <Empty description="No quote requests" />
          ) : (
            <Table rowKey="id" columns={columns} dataSource={rows} />
          )}
        </Card>
      </Space>
    </div>
  );
};
