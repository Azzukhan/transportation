import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createCompany } from "@/api/companies";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Building2, Building, Mail, Phone, UserRound, MapPin, Box, Hash } from "lucide-react";

const initialForm = { name: "", address: "", email: "", phone: "", trn: "", contactPerson: "", poBox: "" };

const AddCompanyPage = () => {
  const qc = useQueryClient();
  const [form, setForm] = useState(initialForm);

  const mutation = useMutation({
    mutationFn: createCompany,
    onSuccess: () => {
      toast.success("Company created successfully!");
      qc.invalidateQueries({ queryKey: ["companies"] });
      setForm(initialForm);
    },
    onError: () => toast.error("Failed to create company."),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  const fieldClass = "h-12 rounded-xl border-border/70 bg-background";

  return (
    <div className="space-y-5 max-w-4xl mx-auto">
      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 rounded-2xl bg-accent/15 border border-accent/25 flex items-center justify-center">
            <Building2 size={26} className="text-accent" />
          </div>
          <div>
            <h1 className="font-display text-4xl font-bold">Add New Company</h1>
            <p className="text-muted-foreground">Register a new client company to your system.</p>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.08}>
        <form onSubmit={handleSubmit} className="bg-card rounded-2xl p-6 md:p-8 shadow-elevated border border-border/60 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="md:col-span-2">
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Building size={15} className="text-accent" /> Company Name *</label>
              <Input
                className={fieldClass}
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Acme Transport Corp"
                required
              />
            </div>

            <div className="md:col-span-2">
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><MapPin size={15} className="text-accent" /> Address *</label>
              <Input
                className={fieldClass}
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
                placeholder="123 Logistics Ave, Suite 100"
                required
              />
            </div>

            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Mail size={15} className="text-accent" /> Email Address *</label>
              <Input
                className={fieldClass}
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="info@company.com"
                type="email"
                required
              />
            </div>

            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Phone size={15} className="text-accent" /> Phone Number</label>
              <Input
                className={fieldClass}
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                placeholder="+971 55 000 0000"
              />
            </div>

            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Hash size={15} className="text-accent" /> TRN *</label>
              <Input
                className={fieldClass}
                value={form.trn}
                onChange={(e) => setForm({ ...form, trn: e.target.value })}
                placeholder="100000000000000"
                required
              />
            </div>

            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><UserRound size={15} className="text-accent" /> Contact Person</label>
              <Input
                className={fieldClass}
                value={form.contactPerson}
                onChange={(e) => setForm({ ...form, contactPerson: e.target.value })}
                placeholder="John Smith"
              />
            </div>

            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Box size={15} className="text-accent" /> PO Box</label>
              <Input
                className={fieldClass}
                value={form.poBox}
                onChange={(e) => setForm({ ...form, poBox: e.target.value })}
                placeholder="PO Box 123"
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button
              type="submit"
              disabled={mutation.isPending}
              className="min-w-48 bg-accent-gradient text-accent-foreground shadow-accent-glow hover:opacity-95 border-0"
            >
              {mutation.isPending ? "Creating..." : "Create Company"}
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => setForm(initialForm)}
              className="text-foreground/80"
            >
              Clear Form
            </Button>
          </div>
        </form>
      </AnimatedSection>
    </div>
  );
};

export default AddCompanyPage;
