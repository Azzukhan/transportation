import {
  ArrowRightOutlined,
  BuildOutlined,
  CarOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
  CompassOutlined,
  FireOutlined,
  GlobalOutlined,
  RocketOutlined,
  SafetyOutlined,
  SafetyCertificateOutlined,
} from "@ant-design/icons";
import { Button, Card, Col, Row, Space, Tag, Typography } from "antd";
import { Link } from "react-router-dom";

import { serviceItems, trustPoints } from "../content/publicContent";
import "../styles/home.css";

const { Title, Paragraph, Text } = Typography;

const kpis = [
  { label: "Active Fleet", value: "38+ Vehicles" },
  { label: "UAE Coverage", value: "7 Emirates" },
  { label: "Completed Jobs", value: "100k+" },
  { label: "Avg Response", value: "30 Minutes" },
];

const whyChoose = [
  {
    icon: <SafetyCertificateOutlined />,
    title: "Disciplined Handling",
    description: "Cargo movement built around safety checks, loading discipline, and route commitment.",
  },
  {
    icon: <ClockCircleOutlined />,
    title: "Reliable Timelines",
    description: "Our operations team follows practical schedule windows for dependable pickup and delivery.",
  },
  {
    icon: <CompassOutlined />,
    title: "Route Precision",
    description: "Local experience across UAE routes with efficient dispatch and destination planning.",
  },
  {
    icon: <FireOutlined />,
    title: "Rapid Support",
    description: "Fast commercial response for new requests, follow-ups, and repeat route planning.",
  },
];

export const HomeRoute = () => {
  return (
    <main className="home-page">
      <section className="home-hero-card fade-slide">
        <div className="home-hero-grid">
          <div className="home-hero-copy">
            <Tag color="blue" className="home-partner-tag">
              Premium Cargo Partner
            </Tag>
            <Title className="home-title">Powering Business Transport Across the UAE With Reliable Execution</Title>
            <Paragraph className="home-subtitle">
              Sikar Cargo delivers purpose-built transport support for businesses, from one-ton pickups to
              full truck movement and exhibition operations.
            </Paragraph>
            <Paragraph className="home-subtitle home-subtitle-secondary">
              Every assignment is planned for route efficiency, protected handling, and on-time completion.
              If your operations depend on dependable freight movement, our team is structured to support it
              with clarity and consistent execution.
            </Paragraph>
            <Space wrap size={12} className="hero-action-row">
              <Link to="/quote">
                <Button type="primary" size="large" icon={<ArrowRightOutlined />}>
                  Request a Quote
                </Button>
              </Link>
              <Link to="/service">
                <Button size="large">Explore Services</Button>
              </Link>
            </Space>

            <div className="hero-trust-block">
              <Text className="hero-trust-title">Why clients trust us</Text>
            </div>
            <div className="hero-trust-line">
              {trustPoints.map((point) => (
                <span key={point}>
                  <CheckCircleFilled /> {point}
                </span>
              ))}
            </div>
          </div>

          <div className="home-hero-visual">
            <img src="/legacy-images/carousel-1.jpg" alt="Sikar Cargo fleet movement" />
            <div className="hero-floating-card hero-float-top">
              <SafetyOutlined />
              <div>
                <strong>Safety-first Dispatch</strong>
                <p>Protected cargo handling standards</p>
              </div>
            </div>
            <div className="hero-floating-card hero-float-mid">
              <GlobalOutlined />
              <div>
                <strong>All Emirates Coverage</strong>
                <p>Commercial transport across UAE</p>
              </div>
            </div>
            <div className="hero-floating-card hero-float-bottom">
              <CarOutlined />
              <div>
                <strong>Dedicated Fleet</strong>
                <p>Pickup and truck options on demand</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="home-stats fade-slide delay-1">
        <Row gutter={[14, 14]}>
          {kpis.map((item) => (
            <Col xs={12} md={6} key={item.label}>
              <Card className="home-stat-card" bordered={false}>
                <Text className="home-stat-label">{item.label}</Text>
                <Title level={3} className="home-stat-value">
                  {item.value}
                </Title>
              </Card>
            </Col>
          ))}
        </Row>
      </section>

      <section className="home-services fade-slide delay-2">
        <div className="section-header">
          <Title level={2}>Transport Services</Title>
          <Link to="/service">View all services</Link>
        </div>
        <Paragraph className="section-lead">
          Select the service model that matches your load volume, route distance, and delivery commitment.
          Each service includes operational planning, dispatch support, and practical communication.
        </Paragraph>
        <Row gutter={[14, 14]}>
          {serviceItems.slice(0, 6).map((service) => (
            <Col xs={24} sm={12} lg={8} key={service.slug}>
              <Link to={`/service/${service.slug}`} className="service-link-card">
                <Card className="home-service-card" bordered={false}>
                  <div className="home-service-image-wrap">
                    <img src={service.image} alt={service.title} loading="lazy" className="home-service-image" />
                  </div>
                  <Text className="home-service-subtitle">{service.subtitle}</Text>
                  <Title level={4}>{service.title}</Title>
                  <Paragraph>{service.summary}</Paragraph>
                  <div className="home-service-meta">
                    <Text className="service-capacity">{service.capacity}</Text>
                    <Text className="home-service-point">{service.bestFor[0]}</Text>
                  </div>
                  <div className="service-link-inline">
                    Get more information <RocketOutlined />
                  </div>
                </Card>
              </Link>
            </Col>
          ))}
        </Row>
      </section>

      <section className="home-why fade-slide delay-3">
        <Title level={2}>Why Businesses Choose Sikar Cargo</Title>
        <Paragraph className="section-lead">
          We combine structured operations, responsive coordination, and a service mindset built for
          long-term commercial partnerships.
        </Paragraph>
        <Row gutter={[14, 14]}>
          {whyChoose.map((item) => (
            <Col xs={24} sm={12} key={item.title}>
              <Card className="why-card" bordered={false}>
                <div className="why-icon">{item.icon}</div>
                <div>
                  <Title level={4}>{item.title}</Title>
                  <Paragraph>{item.description}</Paragraph>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </section>

      <section className="home-exhibition fade-slide delay-4">
        <Row gutter={[14, 14]}>
          <Col xs={24} lg={14}>
            <Card className="home-exhibition-card" bordered={false}>
              <Tag color="gold">Exhibition Material Transfer</Tag>
              <Title level={3}>Before Event Setup and After Event Close-Out Transport</Title>
              <Paragraph>
                We transport exhibition items to venue locations before events begin. After the
                exhibition closes, we handle return movement for materials, wood items, temporary-shop
                dismantled materials, and related cargo.
              </Paragraph>
              <Paragraph className="home-note-line">
                <BuildOutlined /> We do not provide lifting operations.
              </Paragraph>
            </Card>
          </Col>
          <Col xs={24} lg={10}>
            <Card className="home-exhibition-image-card" bordered={false}>
              <img src="/legacy-images/pic_11.png" alt="Exhibition material transfer" />
            </Card>
          </Col>
        </Row>
      </section>

      <section className="home-cta fade-slide delay-4">
        <Title level={2}>Need Immediate Transport Support?</Title>
        <Paragraph>
          Share your route and cargo details. Our operations team will respond with practical options and timelines.
        </Paragraph>
        <Space wrap>
          <Link to="/quote">
            <Button type="primary" size="large">
              Start Quote Request
            </Button>
          </Link>
          <Link to="/live-operations">
            <Button size="large">Live Operations Gallery</Button>
          </Link>
        </Space>
      </section>
    </main>
  );
};
