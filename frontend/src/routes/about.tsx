import { CheckCircleFilled, CrownOutlined, SafetyCertificateOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { Card, Col, Row, Space, Tag, Typography } from "antd";

import { trustPoints } from "../content/publicContent";
import "../styles/public-pages.css";

const { Title, Paragraph, Text } = Typography;

const values = [
  {
    icon: <SafetyCertificateOutlined />,
    title: "Safety Discipline",
    description: "Loading, route selection, and handling standards built for commercial reliability.",
  },
  {
    icon: <ThunderboltOutlined />,
    title: "Operational Speed",
    description: "Fast request acknowledgment with practical planning for urgent and scheduled movement.",
  },
  {
    icon: <CrownOutlined />,
    title: "Service Quality",
    description: "Professional communication, clear commitments, and consistent route execution quality.",
  },
];

const sectors = [
  "Retail and distribution cargo",
  "Project and construction material movement",
  "Exhibition and event material transfers",
  "Commercial warehouse-to-warehouse dispatch",
];

export const AboutRoute = () => {
  return (
    <main className="public-page">
      <section className="public-hero fade-slide">
        <Tag color="blue">About Us</Tag>
        <Title>Built for Businesses That Need Dependable Cargo Movement</Title>
        <Paragraph className="public-section-lead">
          Sikar Cargo Transport supports companies that require disciplined freight movement across UAE.
          Our focus is straightforward: reliable execution, transparent communication, and long-term
          logistics partnership.
        </Paragraph>
      </section>

      <Row gutter={[16, 16]} className="public-grid fade-slide delay-1">
        <Col xs={24} md={14}>
          <Card className="public-card" bordered={false}>
            <Title level={4}>Our Commitment</Title>
            <Paragraph>
              We provide practical transport solutions for daily business movement, heavy cargo dispatch,
              and time-critical operations. Every assignment is planned around route fit, cargo type,
              and delivery timeline.
            </Paragraph>
            <Space direction="vertical" size={10}>
              {trustPoints.map((item) => (
                <Text key={item}>
                  <CheckCircleFilled style={{ color: "#1f5da7", marginRight: 8 }} />
                  {item}
                </Text>
              ))}
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={10}>
          <Card className="public-card about-office-card" bordered={false}>
            <Title level={4}>Head Office</Title>
            <Paragraph>
              G1 Office, Deira Naif, Dubai, UAE
              <br />
              +971 55 238 1722
              <br />
              +971 55 251 6492
              <br />
              Sikarcargo@gmail.com
            </Paragraph>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} className="public-grid fade-slide delay-2">
        {values.map((item) => (
          <Col xs={24} md={8} key={item.title}>
            <Card className="public-card value-card" bordered={false}>
              <div className="value-icon">{item.icon}</div>
              <Title level={4}>{item.title}</Title>
              <Paragraph>{item.description}</Paragraph>
            </Card>
          </Col>
        ))}
      </Row>

      <Card className="public-card public-grid fade-slide delay-3" bordered={false}>
        <Title level={4}>Sectors We Commonly Support</Title>
        <Space direction="vertical" size={8}>
          {sectors.map((item) => (
            <Text key={item}>
              <CheckCircleFilled style={{ color: "#1f5da7", marginRight: 8 }} />
              {item}
            </Text>
          ))}
        </Space>
      </Card>
    </main>
  );
};
