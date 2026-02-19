import { useState } from "react";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { submitContactRequest } from "@/api/publicApi";
import { toast } from "sonner";
import { Mail, Phone, MapPin, Send } from "lucide-react";

const ContactPage = () => {
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    const form = e.currentTarget;
    const data = new FormData(form);
    try {
      await submitContactRequest({
        name: data.get("name") as string,
        email: data.get("email") as string,
        phone: data.get("phone") as string,
        subject: data.get("subject") as string,
        message: data.get("message") as string,
        sourcePage: "contact",
      });
      toast.success("Message sent successfully!");
      form.reset();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to send message. Please try again.";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <section className="bg-hero-gradient py-24">
        <div className="container mx-auto px-4">
          <AnimatedSection>
            <span className="text-accent text-sm font-bold uppercase tracking-wider">Get In Touch</span>
            <h1 className="font-display text-4xl md:text-5xl font-bold text-primary-foreground mt-3 mb-4">
              Contact <span className="text-accent">Us</span>
            </h1>
            <p className="text-primary-foreground/70 text-lg max-w-2xl">
              Talk to our operations team for route planning and service guidance.
            </p>
          </AnimatedSection>
        </div>
      </section>

      <section className="py-24">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            <AnimatedSection className="lg:col-span-2">
              <form onSubmit={handleSubmit} className="bg-card rounded-xl p-8 shadow-card border border-border/50 space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">Full Name</label>
                    <Input name="name" required placeholder="John Doe" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">Email</label>
                    <Input name="email" type="email" required placeholder="john@example.com" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">Phone</label>
                    <Input name="phone" placeholder="+971 55 238 1722" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1.5 block">Subject</label>
                    <Input name="subject" required placeholder="How can we help?" />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Message</label>
                  <Textarea name="message" required rows={5} placeholder="Tell us about your needs..." />
                </div>
                <Button type="submit" disabled={loading} className="bg-accent-gradient text-accent-foreground shadow-accent-glow hover:opacity-90 border-0 px-8">
                  {loading ? "Sending..." : "Send Message"} <Send className="ml-2" size={16} />
                </Button>
              </form>
            </AnimatedSection>

            <AnimatedSection delay={0.2} className="space-y-6">
              {[
                { icon: Phone, title: "Call Us", detail: "+971 55 238 1722 / +971 55 251 6492", sub: "Operations support" },
                { icon: Mail, title: "Email Us", detail: "Sikarcargo@gmail.com", sub: "We reply within 24h" },
                { icon: MapPin, title: "Visit Us", detail: "G1 Office, Deira Naif, Dubai, UAE", sub: "Main office" },
              ].map((item) => (
                <div key={item.title} className="bg-card rounded-xl p-6 shadow-card border border-border/50">
                  <item.icon size={24} className="text-accent mb-3" />
                  <h3 className="font-display font-bold">{item.title}</h3>
                  <p className="text-foreground font-medium text-sm">{item.detail}</p>
                  <p className="text-muted-foreground text-xs">{item.sub}</p>
                </div>
              ))}
            </AnimatedSection>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ContactPage;
