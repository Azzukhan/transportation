import { useEffect, useState } from "react";
import { Button, Card, Empty, Select, Space, Spin, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

import { listContactRequests, updateContactRequestStatus } from "../api/public";
import type { ContactRequestApi } from "../types";
import { toast } from "../utils";

const { Title } = Typography;

const statusOptions = ["new", "in_progress", "resolved", "closed"];

export const ContactRequestsRoute = () => {
  const [rows, setRows] = useState<ContactRequestApi[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const load = async (): Promise<void> => {
    setIsLoading(true);
    try {
      setRows(await listContactRequests());
    } catch {
      toast.error("Failed to load contact requests.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const onStatusChange = async (requestId: number, status: string): Promise<void> => {
    try {
      const updated = await updateContactRequestStatus(requestId, status);
      setRows((current) => current.map((item) => (item.id === requestId ? updated : item)));
      toast.success("Contact request updated.");
    } catch {
      toast.error("Failed to update contact request.");
    }
  };

  const columns: ColumnsType<ContactRequestApi> = [
    { title: "Name", dataIndex: "name" },
    { title: "Email", dataIndex: "email" },
    { title: "Phone", dataIndex: "phone" },
    { title: "Subject", dataIndex: "subject" },
    { title: "Message", dataIndex: "message", ellipsis: true },
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
      title: "Source",
      dataIndex: "source_page",
      render: (value: string) => <Tag>{value}</Tag>,
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
        <Title level={3}>Contact Requests</Title>
      </div>

      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <Button onClick={() => void load()}>Refresh</Button>
        </div>

        <Card>
          {isLoading ? (
            <Spin />
          ) : rows.length === 0 ? (
            <Empty description="No contact requests" />
          ) : (
            <Table rowKey="id" columns={columns} dataSource={rows} />
          )}
        </Card>
      </Space>
    </div>
  );
};
