import { CarOutlined, SendOutlined } from "@ant-design/icons";
import { Button, Card, Col, Form, Input, Row, Select, Space, Statistic, Tag, Typography } from "antd";

import { submitQuoteRequest } from "../api/public";
import { toast } from "../utils";
import "../styles/public-pages.css";

const { Title, Paragraph } = Typography;

type QuoteFormValues = {
  name: string;
  email: string;
  mobile: string;
  freight: string;
  origin: string;
  destination: string;
  note?: string;
};

const freightOptions = ["1 Ton", "3 Ton", "7 Ton", "10 Ton", "Truck"];

export const QuoteRoute = () => {
  const [form] = Form.useForm<QuoteFormValues>();

  const onFinish = async (values: QuoteFormValues): Promise<void> => {
    try {
      await submitQuoteRequest(values);
      toast.success("Quote request submitted successfully.");
      form.resetFields();
    } catch {
      toast.error("Failed to submit quote request.");
    }
  };

  return (
    <main className="public-page">
      <section className="public-hero fade-slide">
        <Tag color="blue">Quotation</Tag>
        <Title>Request Transport Quotation</Title>
        <Paragraph className="public-section-lead">
          Submit your route, freight type, and notes. Our team will share pricing options quickly.
        </Paragraph>
      </section>

      <div className="public-split public-grid fade-slide delay-1">
        <Card className="public-card public-info-card">
          <Title level={4}>Why Request Here</Title>
          <Space direction="vertical" size={10}>
            <Paragraph><CarOutlined /> UAE pickup and truck options</Paragraph>
            <Paragraph><CarOutlined /> Fast response from operations team</Paragraph>
            <Paragraph><CarOutlined /> Route-based practical quotation</Paragraph>
          </Space>
          <Row gutter={10} className="quote-metrics">
            <Col span={12}><Statistic title="Avg Response" value="30m" /></Col>
            <Col span={12}><Statistic title="Coverage" value="7 Emirates" /></Col>
          </Row>
        </Card>

        <Card className="public-card public-form-card">
          <Paragraph className="public-form-intro">
            Provide route and load details. We will respond with a practical quotation quickly.
          </Paragraph>
          <Form<QuoteFormValues> layout="vertical" form={form} onFinish={(v) => void onFinish(v)}>
            <Row gutter={12}>
              <Col xs={24} md={12}>
                <Form.Item label="Name" name="name" rules={[{ required: true }]}> 
                  <Input size="large" />
                </Form.Item>
              </Col>
              <Col xs={24} md={12}>
                <Form.Item label="Email" name="email" rules={[{ required: true, type: "email" }]}> 
                  <Input size="large" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={12}>
              <Col xs={24} md={12}>
                <Form.Item label="Mobile" name="mobile" rules={[{ required: true }]}> 
                  <Input size="large" />
                </Form.Item>
              </Col>
              <Col xs={24} md={12}>
                <Form.Item label="Freight" name="freight" rules={[{ required: true }]}> 
                  <Select
                    size="large"
                    options={freightOptions.map((item) => ({ label: item, value: item }))}
                  />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={12}>
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
            <Form.Item label="Special Note" name="note">
              <Input.TextArea rows={6} />
            </Form.Item>
            <Button type="primary" size="large" icon={<SendOutlined />} htmlType="submit">
              Submit Quote Request
            </Button>
          </Form>
        </Card>
      </div>
    </main>
  );
};
