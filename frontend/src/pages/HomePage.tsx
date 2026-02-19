import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Truck, Package, Boxes, Container, Route, Hammer } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AnimatedSection } from "@/components/AnimatedSection";
import heroImage from "@/assets/hero-transport.jpg";

const stats = [
  { value: "14+ Years", label: "Market Experience", valueClass: "text-3xl md:text-4xl" },
  { value: "200K+", label: "Shipments Delivered", valueClass: "text-3xl md:text-4xl" },
  { value: "24x7", label: "Call Support", valueClass: "text-3xl md:text-4xl" },
  { value: "UAE | KSA | Qatar", label: "Coverage", valueClass: "text-2xl md:text-3xl leading-tight" },
];

const services = [
  { icon: Package, title: "1 Ton Pickup Service", desc: "Light cargo movement for daily distribution and urgent dispatch." },
  { icon: Boxes, title: "3 Ton Pickup Service", desc: "Balanced capacity for branch transfer and route-based B2B operations." },
  { icon: Container, title: "7 Ton Service", desc: "Heavy daily operations for warehouse dispatch and industrial supply movement." },
  { icon: Truck, title: "10 Ton Pickup Service", desc: "Large-batch movement for high-volume and project cargo requirements." },
  { icon: Route, title: "Truck Freight", desc: "Long-haul and large-volume transport for contracted business routes." },
  { icon: Hammer, title: "Exhibition Logistics", desc: "Pre- and post-event material transport. Lifting operations are not included." },
];

const HomePage = () => (
  <div>
    {/* Hero */}
    <section className="relative min-h-[90vh] pt-24 md:pt-28 flex items-center overflow-hidden">
      <div className="absolute inset-0">
        <img src={heroImage} alt="Fleet of trucks on highway" className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-r from-primary/95 via-primary/80 to-primary/40" />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-2xl">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="inline-block bg-accent-gradient text-accent-foreground text-xs font-bold uppercase tracking-wider px-4 py-1.5 rounded-full mb-6">
              Sikar Cargo UAE
            </span>
            <h1 className="font-display text-4xl md:text-6xl font-bold text-primary-foreground leading-tight mb-6">
              Delivering Trust,{" "}
              <span className="text-accent">One Shipment at a Time</span>
            </h1>
            <p className="text-primary-foreground/80 text-lg md:text-xl leading-relaxed mb-8 max-w-xl">
              For over 14 years, Sikar Cargo has delivered 200,000+ shipments with careful handling, clear communication, and a commitment to zero-damage delivery standards.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex flex-wrap gap-4"
          >
            <Link to="/quote">
              <Button size="lg" className="bg-accent-gradient text-accent-foreground shadow-accent-glow hover:opacity-90 border-0 text-base px-8">
                Get a Free Quote <ArrowRight className="ml-2" size={18} />
              </Button>
            </Link>
            <Link to="/service">
              <Button size="lg" variant="outline" className="border-primary-foreground/50 bg-primary-foreground/10 text-primary-foreground hover:bg-primary-foreground/20 text-base px-8">
                Our Services
              </Button>
            </Link>
          </motion.div>
        </div>
      </div>
    </section>

    {/* Stats */}
    <section className="relative -mt-16 z-20">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, i) => (
            <AnimatedSection key={stat.label} delay={i * 0.1}>
              <div className="bg-card rounded-xl p-6 text-center shadow-elevated h-full flex flex-col justify-center">
                <div className={`font-display font-bold text-accent ${stat.valueClass}`}>{stat.value}</div>
                <div className="text-sm text-muted-foreground mt-1">{stat.label}</div>
              </div>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </section>

    {/* Services */}
    <section className="py-24">
      <div className="container mx-auto px-4">
        <AnimatedSection className="text-center mb-16">
          <span className="text-accent text-sm font-bold uppercase tracking-wider">What We Offer</span>
          <h2 className="font-display text-3xl md:text-4xl font-bold mt-3 mb-4">
            What We Actually Do
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Reliable cargo services built on care, accountability, and long-term customer trust.
          </p>
        </AnimatedSection>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((svc, i) => (
            <AnimatedSection key={svc.title} delay={i * 0.08}>
              <div className="group bg-card rounded-xl p-8 shadow-card hover:shadow-elevated transition-all duration-300 hover:-translate-y-1 border border-border/50">
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-5 group-hover:bg-accent-gradient group-hover:shadow-accent-glow transition-all duration-300">
                  <svc.icon size={24} className="text-accent group-hover:text-accent-foreground transition-colors" />
                </div>
                <h3 className="font-display font-bold text-lg mb-2">{svc.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{svc.desc}</p>
              </div>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </section>

    {/* CTA */}
    <section className="py-24 bg-hero-gradient">
      <div className="container mx-auto px-4 text-center">
        <AnimatedSection>
          <h2 className="font-display text-3xl md:text-4xl font-bold text-primary-foreground mb-4">
            Need Transport Support?
          </h2>
          <p className="text-primary-foreground/70 text-lg max-w-xl mx-auto mb-8">
            Share your pickup and destination details. Our team responds quickly with practical route planning and market-rate pricing.
          </p>
          <Link to="/quote">
            <Button size="lg" className="bg-accent-gradient text-accent-foreground shadow-accent-glow hover:opacity-90 border-0 text-base px-10">
              Request a Quote <ArrowRight className="ml-2" size={18} />
            </Button>
          </Link>
        </AnimatedSection>
      </div>
    </section>
  </div>
);

export default HomePage;
