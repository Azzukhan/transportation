import { ArrowRightOutlined, CheckCircleFilled } from "@ant-design/icons";
import { Button, Card, Col, Row, Space, Tag, Typography } from "antd";
import { Link } from "react-router-dom";

import { serviceItems } from "../content/publicContent";
import "../styles/public-pages.css";

const { Title, Paragraph, Text } = Typography;

export const ServiceRoute = () => {
  return (
    <main className="public-page">
      <section className="public-hero fade-slide">
        <Tag color="gold">Service Portfolio</Tag>
        <Title>Complete Freight Services for Every Business Scale</Title>
        <Paragraph>
          Choose the service model that fits your cargo size, route pattern, and delivery timeline.
          Every service card below opens full details.
        </Paragraph>
        <Paragraph>
          From daily pickup assignments to high-volume freight movement, each service is designed with
          practical route planning, disciplined execution, and dependable communication.
        </Paragraph>
      </section>

      <Row gutter={[16, 16]} className="public-grid fade-slide delay-1">
        {serviceItems.map((service) => (
          <Col xs={24} md={12} lg={8} key={service.slug}>
            <Card className="public-card service-portfolio-card" bordered={false}>
              <div className="service-portfolio-image-wrap">
                <img src={service.image} alt={service.title} loading="lazy" className="service-portfolio-image" />
              </div>
              <div className="service-portfolio-top">
                <Text className="service-portfolio-capacity">{service.capacity}</Text>
                <Text className="service-portfolio-subtitle">{service.subtitle}</Text>
              </div>
              <Title level={4}>{service.title}</Title>
              <Paragraph>{service.summary}</Paragraph>
              <Space direction="vertical" size={6} className="service-portfolio-points">
                {service.bestFor.slice(0, 2).map((point) => (
                  <Text key={point}>
                    <CheckCircleFilled /> {point}
                  </Text>
                ))}
              </Space>
              <Link to={`/service/${service.slug}`}>
                <Button type="link" className="service-detail-btn" icon={<ArrowRightOutlined />}>
                  Get more information
                </Button>
              </Link>
            </Card>
          </Col>
        ))}
      </Row>
    </main>
  );
};
