import { Button, Card, Col, Form, Input, InputNumber, Row, Select, Typography } from "antd";

import { createTrip } from "../api/trips";
import { useCompanies } from "../hooks";
import { toast } from "../utils";
import type { TripCreateInput } from "../types";

const { Title, Paragraph } = Typography;

export const AddTripRoute = () => {
  const [form] = Form.useForm<TripCreateInput>();
  const { companies } = useCompanies();

  const onFinish = async (values: TripCreateInput): Promise<void> => {
    try {
      await createTrip(values);
      toast.success("Trip added successfully.");
      form.resetFields();
    } catch {
      toast.error("Failed to add trip.");
    }
  };

  return (
    <div className="admin-page admin-fade">
      <div className="admin-page-head">
        <Title level={3}>Add Trip</Title>
        <Paragraph>Create transport trip records for operational and invoice workflows.</Paragraph>
      </div>

      <Card>
        <Form<TripCreateInput>
          form={form}
          layout="vertical"
          onFinish={(values) => void onFinish(values)}
          style={{ marginTop: 6 }}
        >
          <Row gutter={12} className="admin-grid-gap">
            <Col xs={24} md={12}>
              <Form.Item label="Company" name="companyId" rules={[{ required: true }]}>
                <Select
                  size="large"
                  options={companies.map((company) => ({ label: company.name, value: company.id }))}
                  showSearch
                  optionFilterProp="label"
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Date" name="date" rules={[{ required: true }]}>
                <Input size="large" type="date" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12} className="admin-grid-gap">
            <Col xs={24} md={12}>
              <Form.Item label="Freight" name="freight" rules={[{ required: true }]}>
                <Select
                  size="large"
                  options={["1 Ton", "3 Ton", "7 Ton", "10 Ton", "Truck"].map((item) => ({
                    label: item,
                    value: item,
                  }))}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Driver" name="driver" rules={[{ required: true }]}>
                <Input size="large" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12} className="admin-grid-gap">
            <Col xs={24} md={12}>
              <Form.Item label="Origin" name="origin" rules={[{ required: true }]}>
                <Input size="large" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Destination" name="destination" rules={[{ required: true }]}>
                <Input size="large" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12} className="admin-grid-gap">
            <Col xs={24} md={12}>
              <Form.Item label="Amount" name="amount" rules={[{ required: true }]}>
                <InputNumber<number>
                  size="large"
                  style={{ width: "100%" }}
                  min={0}
                  step={0.01}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item label="Toll Gate" name="tollGate" initialValue={0} rules={[{ required: true }]}>
                <InputNumber<number>
                  size="large"
                  style={{ width: "100%" }}
                  min={0}
                  step={0.01}
                />
              </Form.Item>
            </Col>
          </Row>

          <Button type="primary" htmlType="submit" size="large">
            Save Trip
          </Button>
        </Form>
      </Card>
    </div>
  );
};
