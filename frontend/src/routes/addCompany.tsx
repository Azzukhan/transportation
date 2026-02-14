import { Button, Card, Form, Input, Typography } from "antd";
import { useNavigate } from "react-router-dom";

import { useCompanies } from "../hooks";
import type { CompanyCreateInput } from "../types";

const { Title, Paragraph } = Typography;

export const AddCompanyRoute = () => {
  const navigate = useNavigate();
  const { addCompany } = useCompanies();
  const [form] = Form.useForm<CompanyCreateInput>();

  const onFinish = async (values: CompanyCreateInput): Promise<void> => {
    const success = await addCompany(values);
    if (!success) {
      return;
    }
    form.resetFields();
    navigate("/dashboard", { replace: true });
  };

  return (
    <div className="admin-page admin-fade">
      <div className="admin-page-head">
        <Title level={3}>Add Company</Title>
        <Paragraph>Add a new customer company profile and return to dashboard.</Paragraph>
      </div>

      <Card>
        <Form<CompanyCreateInput>
          layout="vertical"
          form={form}
          onFinish={(values) => void onFinish(values)}
          style={{ marginTop: 6 }}
        >
          <Form.Item label="Company Name" name="name" rules={[{ required: true }]}>
            <Input size="large" />
          </Form.Item>

          <Form.Item label="Address" name="address" rules={[{ required: true }]}>
            <Input.TextArea rows={3} />
          </Form.Item>

          <Form.Item label="Email" name="email" rules={[{ required: true, type: "email" }]}>
            <Input size="large" />
          </Form.Item>

          <Form.Item label="Phone" name="phone" rules={[{ required: true }]}>
            <Input size="large" />
          </Form.Item>

          <Form.Item label="Contact Person" name="contactPerson" rules={[{ required: true }]}>
            <Input size="large" />
          </Form.Item>

          <Form.Item label="PO Box" name="poBox" rules={[{ required: true }]}>
            <Input size="large" />
          </Form.Item>

          <Button type="primary" htmlType="submit" size="large">
            Save Company
          </Button>
        </Form>
      </Card>
    </div>
  );
};
