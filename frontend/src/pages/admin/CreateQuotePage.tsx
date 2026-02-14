import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { submitQuoteRequest } from "@/api/publicApi";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { MessageSquare, UserRound, Mail, Phone, Route, Package } from "lucide-react";

const initialForm = {
  name: "",
  email: "",
  mobile: "",
  freight: "",
  origin: "",
  destination: "",
  note: "",
};

const CreateQuotePage = () => {
  const qc = useQueryClient();
  const [form, setForm] = useState(initialForm);

  const mutation = useMutation({
    mutationFn: submitQuoteRequest,
    onSuccess: () => {
      toast.success("Quote request created successfully!");
      qc.invalidateQueries({ queryKey: ["quote-requests"] });
      setForm(initialForm);
    },
    onError: () => toast.error("Failed to create quote request."),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 rounded-2xl bg-accent/15 border border-accent/25 flex items-center justify-center">
            <MessageSquare size={26} className="text-accent" />
          </div>
          <div>
            <h1 className="font-display text-4xl font-bold">Create Quote Request</h1>
            <p className="text-muted-foreground">Create a quote request manually when a company calls directly.</p>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.08}>
        <form onSubmit={handleSubmit} className="bg-card rounded-2xl p-6 md:p-8 shadow-elevated border border-border/60 space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><UserRound size={15} className="text-accent" /> Name *</label>
              <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Company contact name" required />
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Mail size={15} className="text-accent" /> Email *</label>
              <Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="contact@company.com" required />
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Phone size={15} className="text-accent" /> Mobile *</label>
              <Input value={form.mobile} onChange={(e) => setForm({ ...form, mobile: e.target.value })} placeholder="+971 55 000 0000" required />
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Package size={15} className="text-accent" /> Freight Type *</label>
              <Input value={form.freight} onChange={(e) => setForm({ ...form, freight: e.target.value })} placeholder="1 Ton / 3 Ton / 7 Ton / Truck" required />
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Route size={15} className="text-accent" /> Origin *</label>
              <Input value={form.origin} onChange={(e) => setForm({ ...form, origin: e.target.value })} placeholder="Pickup location" required />
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Route size={15} className="text-accent" /> Destination *</label>
              <Input value={form.destination} onChange={(e) => setForm({ ...form, destination: e.target.value })} placeholder="Delivery location" required />
            </div>
          </div>
          <div>
            <label className="text-sm font-semibold mb-2 block">Notes</label>
            <Textarea value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} rows={5} placeholder="Any special requirements, timings, or quote notes..." />
          </div>

          <div className="flex flex-wrap gap-3">
            <Button type="submit" disabled={mutation.isPending} className="bg-accent-gradient text-accent-foreground border-0">
              {mutation.isPending ? "Creating..." : "Create Quote Request"}
            </Button>
            <Button type="button" variant="ghost" onClick={() => setForm(initialForm)}>
              Clear Form
            </Button>
          </div>
        </form>
      </AnimatedSection>
    </div>
  );
};

export default CreateQuotePage;
