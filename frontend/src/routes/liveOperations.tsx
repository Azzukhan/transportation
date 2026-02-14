import { CameraOutlined } from "@ant-design/icons";
import { Carousel, Col, Image, Row, Segmented, Tag, Typography } from "antd";
import { useMemo, useState } from "react";

import { operationGallery } from "../content/publicContent";
import "../styles/public-pages.css";

const { Title, Paragraph } = Typography;

type GalleryFilter = "all" | "fleet" | "pickup" | "heavy" | "exhibition";

const topStrip = operationGallery.slice(0, 7);
const bottomStrip = operationGallery.slice(7);

export const LiveOperationsRoute = () => {
  const [filter, setFilter] = useState<GalleryFilter>("all");

  const visibleItems = useMemo(() => {
    if (filter === "all") {
      return operationGallery;
    }
    return operationGallery.filter((item) => item.category === filter);
  }, [filter]);

  return (
    <main className="public-page">
      <section className="public-hero fade-slide">
        <Tag color="geekblue">Live Operations</Tag>
        <Title>Operations Gallery</Title>
        <Paragraph>
          Real movement visuals from active cargo routes, pickup jobs, heavy transport, and exhibition
          material transfers before and after event timelines across the UAE.
        </Paragraph>
      </section>

      <section className="ops-carousel-wrap fade-slide delay-1">
        <Carousel autoplay autoplaySpeed={3000} dots className="ops-carousel">
          {operationGallery.map((item, index) => (
            <div key={item.src}>
              <div className="ops-carousel-slide">
                <img src={item.src} alt={`Live operation ${index + 1}`} className="ops-carousel-image" />
              </div>
            </div>
          ))}
        </Carousel>
      </section>

      <section className="ops-marquee-section fade-slide delay-2" aria-label="Moving operations image strip">
        <div className="ops-marquee-track">
          {[...topStrip, ...topStrip].map((item, idx) => (
            <img key={`${item.src}-${idx}`} src={item.src} alt={item.title} className="ops-marquee-image" />
          ))}
        </div>
        <div className="ops-marquee-track reverse">
          {[...bottomStrip, ...bottomStrip].map((item, idx) => (
            <img key={`${item.src}-${idx}`} src={item.src} alt={item.title} className="ops-marquee-image" />
          ))}
        </div>
      </section>

      <section className="ops-grid-section fade-slide delay-3">
        <div className="ops-grid-head">
          <Title level={3}>Live Shots</Title>
          <Segmented<GalleryFilter>
            value={filter}
            onChange={(value) => setFilter(value as GalleryFilter)}
            options={[
              { label: "All", value: "all" },
              { label: "Fleet", value: "fleet" },
              { label: "Pickup", value: "pickup" },
              { label: "Heavy", value: "heavy" },
              { label: "Exhibition", value: "exhibition" },
            ]}
          />
        </div>

        <Image.PreviewGroup>
          <Row gutter={[14, 14]}>
            {visibleItems.map((item, index) => (
              <Col xs={12} md={8} lg={6} key={`${item.src}-${index}`}>
                <div className="ops-grid-card">
                  <Image src={item.src} alt={item.title} className="ops-grid-image" preview />
                  <span>
                    <CameraOutlined /> {item.title}
                  </span>
                </div>
              </Col>
            ))}
          </Row>
        </Image.PreviewGroup>
      </section>
    </main>
  );
};
