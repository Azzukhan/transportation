import { useState } from "react";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { submitQuoteRequest } from "@/api/publicApi";
import { toast } from "sonner";
import { Send, CheckCircle } from "lucide-react";

const QuotePage = () => {
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    const form = e.currentTarget;
    const data = new FormData(form);
    try {
      await submitQuoteRequest({
        name: data.get("name") as string,
        email: data.get("email") as string,
        mobile: data.get("mobile") as string,
        freight: data.get("freight") as string,
        origin: data.get("origin") as string,
        destination: data.get("destination") as string,
        note: data.get("note") as string,
      });
      setSubmitted(true);
    } catch {
      toast.error("Failed to submit quote request. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <AnimatedSection className="text-center max-w-md mx-auto">
          <CheckCircle size={64} className="text-accent mx-auto mb-4" />
          <h2 className="font-display text-2xl font-bold mb-2">Quote Requested!</h2>
          <p className="text-muted-foreground">We've received your request and will get back to you within 24 hours with a personalized quote.</p>
        </AnimatedSection>
      </div>
    );
  }

  return (
    <div>
      <section className="bg-hero-gradient py-24">
        <div className="container mx-auto px-4">
          <AnimatedSection>
            <span className="text-accent text-sm font-bold uppercase tracking-wider">Free Quote</span>
            <h1 className="font-display text-4xl md:text-5xl font-bold text-primary-foreground mt-3 mb-4">
              Get Your <span className="text-accent">Free Quote</span>
            </h1>
            <p className="text-primary-foreground/70 text-lg max-w-2xl">
              Tell us about your shipment and we'll provide a competitive quote within 24 hours.
            </p>
          </AnimatedSection>
        </div>
      </section>

      <section className="py-24">
        <div className="container mx-auto px-4 max-w-2xl">
          <AnimatedSection>
            <form onSubmit={handleSubmit} className="bg-card rounded-xl p-8 shadow-elevated border border-border/50 space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Full Name *</label>
                  <Input name="name" required placeholder="John Doe" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Email *</label>
                  <Input name="email" type="email" required placeholder="john@example.com" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Mobile *</label>
                  <Input name="mobile" required placeholder="+971 55 238 1722" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Freight Type *</label>
                  <Input name="freight" required placeholder="1 Ton / 3 Ton / 7 Ton / 10 Ton / Truck / Exhibition" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Origin *</label>
                  <Input name="origin" required placeholder="Pickup city" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Destination *</label>
                  <Input name="destination" required placeholder="Delivery city" />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Additional Notes</label>
                <Textarea name="note" rows={4} placeholder="Any special requirements..." />
              </div>
              <Button type="submit" disabled={loading} className="w-full bg-accent-gradient text-accent-foreground shadow-accent-glow hover:opacity-90 border-0">
                {loading ? "Submitting..." : "Submit Quote Request"} <Send className="ml-2" size={16} />
              </Button>
            </form>
          </AnimatedSection>
        </div>
      </section>
    </div>
  );
};

export default QuotePage;
