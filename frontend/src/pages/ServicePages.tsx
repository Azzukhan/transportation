import { Link, useParams } from "react-router-dom";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Truck, Package, Boxes, Container, Route, Hammer, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

const allServices = [
  {
    slug: "one-ton-pickup",
    icon: Package,
    title: "1 Ton Pickup Service",
    short: "Fast local and inter-city pickup support.",
    details:
      "Ideal for compact freight that needs same-day handling. Supports retail deliveries, supplier dispatch, maintenance cargo, and daily replenishment.",
  },
  {
    slug: "three-ton-pickup",
    icon: Boxes,
    title: "3 Ton Pickup Service",
    short: "Balanced volume and speed for B2B operations.",
    details:
      "Best for wholesale transfers, office movement support, and scheduled distribution routes where both capacity and agility are needed.",
  },
  {
    slug: "seven-ton-service",
    icon: Container,
    title: "7 Ton Service",
    short: "High-capacity movement for industrial and warehouse needs.",
    details:
      "Operationally strong option for industrial material movement, warehouse distribution, and repeat B2B dispatch with practical scheduling.",
  },
  {
    slug: "ten-ton-pickup",
    icon: Truck,
    title: "10 Ton Pickup Service",
    short: "Heavy-duty support for large shipment batches.",
    details:
      "Designed for project sites and high-volume routes, including oversized delivery plans and repeated heavy dispatch operations.",
  },
  {
    slug: "truck-freight",
    icon: Route,
    title: "Truck Freight",
    short: "Long-haul and large-volume transport support.",
    details:
      "Purpose-built truck operations for long-distance and high-volume cargo movement, contracted business routes, and consolidated freight.",
  },
  {
    slug: "exhibition-logistics",
    icon: Hammer,
    title: "Exhibition Logistics",
    short: "Pre- and post-exhibition material transport.",
    details:
      "We move exhibition materials before event start and after close-out, including stand and temporary-shop materials. Note: lifting operations are not provided.",
  },
];

export const ServiceListPage = () => (
  <div>
    <section className="bg-hero-gradient py-24">
      <div className="container mx-auto px-4">
        <AnimatedSection>
          <span className="text-accent text-sm font-bold uppercase tracking-wider">Our Services</span>
          <h1 className="font-display text-4xl md:text-5xl font-bold text-primary-foreground mt-3 mb-4">
            Active Service <span className="text-accent">Portfolio</span>
          </h1>
        </AnimatedSection>
      </div>
    </section>

    <section className="py-24">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {allServices.map((svc, i) => (
            <AnimatedSection key={svc.slug} delay={i * 0.08}>
              <Link to={`/service/${svc.slug}`} className="block group">
                <div className="bg-card rounded-xl p-8 shadow-card hover:shadow-elevated transition-all duration-300 hover:-translate-y-1 border border-border/50 h-full">
                  <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-5 group-hover:bg-accent-gradient transition-all">
                    <svc.icon size={24} className="text-accent group-hover:text-accent-foreground transition-colors" />
                  </div>
                  <h3 className="font-display font-bold text-lg mb-2">{svc.title}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed mb-4">{svc.short}</p>
                  <span className="text-accent text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
                    Learn More <ArrowRight size={14} />
                  </span>
                </div>
              </Link>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </section>
  </div>
);

export const ServiceDetailPage = () => {
  const { slug } = useParams();
  const svc = allServices.find((s) => s.slug === slug);

  if (!svc) return <div className="min-h-screen flex items-center justify-center"><p>Service not found.</p></div>;

  return (
    <div>
      <section className="bg-hero-gradient py-24">
        <div className="container mx-auto px-4">
          <AnimatedSection>
            <Link to="/service" className="text-accent text-sm mb-4 inline-block hover:underline">← All Services</Link>
            <div className="flex items-center gap-4 mb-4">
              <div className="w-14 h-14 bg-accent-gradient rounded-xl flex items-center justify-center shadow-accent-glow">
                <svc.icon size={28} className="text-accent-foreground" />
              </div>
              <h1 className="font-display text-4xl font-bold text-primary-foreground">{svc.title}</h1>
            </div>
          </AnimatedSection>
        </div>
      </section>

      <section className="py-24">
        <div className="container mx-auto px-4 max-w-3xl">
          <AnimatedSection>
            <p className="text-lg leading-relaxed text-muted-foreground mb-8">{svc.details}</p>
            <Link to="/quote">
              <Button className="bg-accent-gradient text-accent-foreground shadow-accent-glow hover:opacity-90 border-0">
                Get a Quote for {svc.title} <ArrowRight className="ml-2" size={16} />
              </Button>
            </Link>
          </AnimatedSection>
        </div>
      </section>
    </div>
  );
};
