import { AnimatedSection } from "@/components/AnimatedSection";
import { Users, Target, Award, TrendingUp } from "lucide-react";

const values = [
  { icon: Target, title: "Careful Handling", desc: "Every item is handled with proper inspection before movement." },
  { icon: Users, title: "Trust First", desc: "We take full responsibility for goods during transport operations." },
  { icon: Award, title: "Quality With Market Rate", desc: "Professional service standard with practical market pricing." },
  { icon: TrendingUp, title: "High Repeat Orders", desc: "Most of our business is repeated because of consistent delivery trust." },
];

const AboutPage = () => (
  <div>
    <section className="bg-hero-gradient py-24">
      <div className="container mx-auto px-4">
        <AnimatedSection>
          <span className="text-accent text-sm font-bold uppercase tracking-wider">About Us</span>
          <h1 className="font-display text-4xl md:text-5xl font-bold text-primary-foreground mt-3 mb-4">
            Built for Practical <span className="text-accent">Transport Work</span>
          </h1>
          <p className="text-primary-foreground/70 text-lg max-w-2xl">
            For the last 14 years, we have supported businesses with dependable cargo movement and long-term service trust.
          </p>
        </AnimatedSection>
      </div>
    </section>

    <section className="py-24">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <AnimatedSection>
            <h2 className="font-display text-3xl font-bold mb-6">Our Story</h2>
            <div className="space-y-4 text-muted-foreground leading-relaxed">
              <p>
                We have been serving this market for the last 14 years and have delivered more than 200,000 shipments with a strong no-complaint and no-damage track record.
              </p>
              <p>
                Our team takes full responsibility for every shipment and follows careful handling with proper inspection before dispatch.
              </p>
              <p>
                We earn trust through timely delivery, clear communication, and safe cargo execution.
              </p>
              <p>
                Our order repeat rate is close to 100%, and we maintain strong service standards with market-rate pricing.
              </p>
              <p>
                We provide cargo services across the UAE and also support international cargo routes to Saudi Arabia and Qatar.
              </p>
              <p>
                Head Office: G1 Office, Deira Naif, Dubai, UAE.
              </p>
            </div>
          </AnimatedSection>

          <AnimatedSection delay={0.2}>
            <div className="grid grid-cols-2 gap-4">
              {values.map((v, i) => (
                <div key={v.title} className="bg-card rounded-xl p-6 shadow-card border border-border/50">
                  <v.icon size={28} className="text-accent mb-3" />
                  <h3 className="font-display font-bold text-sm mb-1">{v.title}</h3>
                  <p className="text-muted-foreground text-xs leading-relaxed">{v.desc}</p>
                </div>
              ))}
            </div>
          </AnimatedSection>
        </div>
      </div>
    </section>
  </div>
);

export default AboutPage;
