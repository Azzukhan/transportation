import { ClockCircleOutlined, RocketOutlined, SafetyCertificateOutlined, TeamOutlined } from "@ant-design/icons";
import { Card, Col, Row, Tag, Typography } from "antd";

import "../styles/public-pages.css";

const { Title, Paragraph } = Typography;

const highlights = [
  {
    icon: <ClockCircleOutlined style={{ fontSize: 28, color: "#1f6ed2" }} />,
    title: "Fast Commercial Response",
    description: "Quick acknowledgment for quote and support requests during active business hours.",
  },
  {
    icon: <SafetyCertificateOutlined style={{ fontSize: 28, color: "#1f6ed2" }} />,
    title: "Reliable Handling Standards",
    description: "Disciplined loading and movement process designed for cargo safety and stability.",
  },
  {
    icon: <RocketOutlined style={{ fontSize: 28, color: "#1f6ed2" }} />,
    title: "Scalable Service Range",
    description: "From compact pickup loads to heavy truck movement based on your operational need.",
  },
  {
    icon: <TeamOutlined style={{ fontSize: 28, color: "#1f6ed2" }} />,
    title: "Dedicated Operations Team",
    description: "Real people supporting route planning, dispatch communication, and delivery tracking.",
  },
];

export const FeatureRoute = () => {
  return (
    <main className="public-page">
      <section className="public-hero fade-slide">
        <Tag color="geekblue">Why Us</Tag>
        <Title>Why Companies Prefer Sikar Cargo</Title>
        <Paragraph>
          Premium logistics support with practical execution quality, fast communication, and consistent
          freight movement support across UAE.
        </Paragraph>
      </section>

      <Row gutter={[14, 14]} className="public-grid fade-slide delay-1">
        {highlights.map((feature) => (
          <Col xs={24} md={12} key={feature.title}>
            <Card className="public-card" bordered={false}>
              {feature.icon}
              <Title level={4} style={{ marginTop: 12 }}>{feature.title}</Title>
              <Paragraph>{feature.description}</Paragraph>
            </Card>
          </Col>
        ))}
      </Row>
    </main>
  );
};
