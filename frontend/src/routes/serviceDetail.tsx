import { CheckCircleFilled, EnvironmentOutlined } from "@ant-design/icons";
import { Button, Card, Col, Row, Space, Tag, Typography } from "antd";
import { Link, Navigate, useParams } from "react-router-dom";

import { serviceItems } from "../content/publicContent";
import "../styles/public-pages.css";

const { Title, Paragraph, Text } = Typography;

export const ServiceDetailRoute = () => {
  const { slug } = useParams<{ slug: string }>();
  const service = serviceItems.find((item) => item.slug === slug);

  if (!service) {
    return <Navigate to="/service" replace />;
  }

  return (
    <main className="public-page">
      <section className="public-hero fade-slide">
        <Tag color="blue">Service Detail</Tag>
        <Title>{service.title}</Title>
        <Paragraph>{service.description}</Paragraph>
      </section>

      <Row gutter={[16, 16]} className="public-grid fade-slide delay-1">
        <Col xs={24} lg={11}>
          <Card className="public-card detail-image-card" bordered={false}>
            <img src={service.image} alt={service.title} className="detail-hero-image" />
          </Card>
        </Col>
        <Col xs={24} lg={13}>
          <Card className="public-card" bordered={false}>
            <Title level={4}>Service Snapshot</Title>
            <Space direction="vertical" size={10}>
              <Text>
                <EnvironmentOutlined /> Coverage across all major UAE routes.
              </Text>
              <Text>
                <CheckCircleFilled /> Capacity: {service.capacity}
              </Text>
              <Text>
                <CheckCircleFilled /> {service.subtitle}
              </Text>
              {service.slug === "exhibition-logistics" ? (
                <Text strong>
                  <CheckCircleFilled /> Note: Transport support only, no lifting operations.
                </Text>
              ) : null}
            </Space>

            <Title level={5} style={{ marginTop: 18 }}>Best For</Title>
            <Space direction="vertical" size={8}>
              {service.bestFor.map((item) => (
                <Text key={item}>
                  <CheckCircleFilled style={{ color: "#1f5da7", marginRight: 8 }} />
                  {item}
                </Text>
              ))}
            </Space>

            <Title level={5} style={{ marginTop: 18 }}>Key Highlights</Title>
            <Space direction="vertical" size={8}>
              {service.highlights.map((item) => (
                <Text key={item}>
                  <CheckCircleFilled style={{ color: "#1f5da7", marginRight: 8 }} />
                  {item}
                </Text>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>

      <section className="detail-cta fade-slide delay-2">
        <Title level={3}>Need Pricing for This Service?</Title>
        <Paragraph>
          Send your route details now and receive a practical quotation from our team.
        </Paragraph>
        <Space>
          <Link to="/quote">
            <Button type="primary" size="large">Get Quote</Button>
          </Link>
          <Link to="/service">
            <Button size="large">All Services</Button>
          </Link>
        </Space>
      </section>
    </main>
  );
};
