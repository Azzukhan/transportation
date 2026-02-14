import { EnvironmentOutlined, MailOutlined, PhoneOutlined } from "@ant-design/icons";
import { Button, Card, Col, Form, Input, Row, Space, Tag, Typography } from "antd";

import { submitContactRequest } from "../api/public";
import { toast } from "../utils";
import "../styles/public-pages.css";

const { Title, Paragraph, Text } = Typography;

type ContactFormValues = {
  name: string;
  email: string;
  phone: string;
  subject: string;
  message: string;
};

export const ContactRoute = () => {
  const [form] = Form.useForm<ContactFormValues>();

  const onFinish = async (values: ContactFormValues): Promise<void> => {
    try {
      await submitContactRequest(values);
      toast.success("Your contact request has been submitted.");
      form.resetFields();
    } catch {
      toast.error("Failed to submit contact request.");
    }
  };

  return (
    <main className="public-page">
      <section className="public-hero fade-slide">
        <Tag color="cyan">Contact</Tag>
        <Title>Talk to Our Operations Team</Title>
        <Paragraph className="public-section-lead">
          Share your transport requirement, and we will respond with route and service guidance.
        </Paragraph>
      </section>

      <div className="public-split public-grid fade-slide delay-1">
        <Card className="public-card public-info-card">
          <Title level={4}>Office & Support</Title>
          <Space direction="vertical" size={12}>
            <Text><EnvironmentOutlined /> G1 Office, Deira Naif, Dubai, UAE</Text>
            <Text><PhoneOutlined /> +971 55 238 1722</Text>
            <Text><PhoneOutlined /> +971 55 251 6492</Text>
            <Text><MailOutlined /> Sikarcargo@gmail.com</Text>
          </Space>
        </Card>

        <Card className="public-card public-form-card">
          <Paragraph className="public-form-intro">
            Fill in the form below. Our team will get back to you with route and service guidance.
          </Paragraph>
          <Form<ContactFormValues> layout="vertical" form={form} onFinish={(values) => void onFinish(values)}>
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
                <Form.Item label="Phone" name="phone" rules={[{ required: true }]}>
                  <Input size="large" />
                </Form.Item>
              </Col>
              <Col xs={24} md={12}>
                <Form.Item label="Subject" name="subject" rules={[{ required: true }]}>
                  <Input size="large" />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item label="Message" name="message" rules={[{ required: true, min: 5 }]}>
              <Input.TextArea rows={6} />
            </Form.Item>
            <Button type="primary" size="large" htmlType="submit">
              Send Message
            </Button>
          </Form>
        </Card>
      </div>
    </main>
  );
};
