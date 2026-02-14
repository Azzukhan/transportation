import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createTrip } from "@/api/trips";
import { listCompanies } from "@/api/companies";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Truck, Building2, Calendar, Package, MapPin, Navigation, CircleDollarSign, UserRound, Landmark } from "lucide-react";

const initialForm = {
  companyId: "",
  date: "",
  freight: "",
  origin: "",
  destination: "",
  amount: "",
  tollGate: "",
  driver: "",
};

const AddTripPage = () => {
  const qc = useQueryClient();
  const companies = useQuery({ queryKey: ["companies"], queryFn: listCompanies });
  const [form, setForm] = useState(initialForm);

  const completed = useMemo(() => {
    const values = Object.values(form);
    return values.filter((v) => v.trim() !== "").length;
  }, [form]);

  const mutation = useMutation({
    mutationFn: createTrip,
    onSuccess: () => {
      toast.success("Trip created successfully!");
      qc.invalidateQueries({ queryKey: ["trips"] });
      setForm(initialForm);
    },
    onError: () => toast.error("Failed to create trip."),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      companyId: Number(form.companyId),
      date: form.date,
      freight: form.freight,
      origin: form.origin,
      destination: form.destination,
      amount: Number(form.amount),
      tollGate: Number(form.tollGate),
      driver: form.driver,
    });
  };

  const fieldClass = "h-12 rounded-xl border-border/70 bg-background";

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 rounded-2xl bg-accent/15 border border-accent/25 flex items-center justify-center">
            <Truck size={26} className="text-accent" />
          </div>
          <div>
            <h1 className="font-display text-4xl font-bold">Add New Trip</h1>
            <p className="text-muted-foreground">Record a new transportation trip.</p>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.08}>
        <div className="bg-card rounded-2xl p-6 md:p-8 shadow-elevated border border-border/60 space-y-6">
          <div>
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-muted-foreground">Form Progress</span>
              <span className="text-muted-foreground">{completed}/8 fields</span>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <div className="h-full bg-accent-gradient transition-all" style={{ width: `${(completed / 8) * 100}%` }} />
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Building2 size={15} className="text-accent" /> Company *</label>
              <Select value={form.companyId} onValueChange={(v) => setForm({ ...form, companyId: v })}>
                <SelectTrigger className={fieldClass}>
                  <SelectValue placeholder="Select a company" />
                </SelectTrigger>
                <SelectContent>
                  {companies.data?.map((c) => (
                    <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Calendar size={15} className="text-accent" /> Date *</label>
                <Input className={fieldClass} type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
              </div>
              <div>
                <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Package size={15} className="text-accent" /> Freight Type *</label>
                <Input className={fieldClass} value={form.freight} onChange={(e) => setForm({ ...form, freight: e.target.value })} placeholder="General cargo" required />
              </div>
              <div>
                <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><MapPin size={15} className="text-accent" /> Origin *</label>
                <Input className={fieldClass} value={form.origin} onChange={(e) => setForm({ ...form, origin: e.target.value })} placeholder="Pickup city" required />
              </div>
              <div>
                <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Navigation size={15} className="text-accent" /> Destination *</label>
                <Input className={fieldClass} value={form.destination} onChange={(e) => setForm({ ...form, destination: e.target.value })} placeholder="Delivery city" required />
              </div>
              <div>
                <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><CircleDollarSign size={15} className="text-accent" /> Amount (AED) *</label>
                <Input className={fieldClass} type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
              </div>
              <div>
                <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Landmark size={15} className="text-accent" /> Toll Gate (AED)</label>
                <Input className={fieldClass} type="number" step="0.01" value={form.tollGate} onChange={(e) => setForm({ ...form, tollGate: e.target.value })} />
              </div>
              <div className="md:col-span-2">
                <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><UserRound size={15} className="text-accent" /> Driver *</label>
                <Input className={fieldClass} value={form.driver} onChange={(e) => setForm({ ...form, driver: e.target.value })} placeholder="Driver full name" required />
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3 pt-1">
              <Button type="submit" disabled={mutation.isPending} className="min-w-44 bg-accent-gradient text-accent-foreground shadow-accent-glow hover:opacity-95 border-0">
                {mutation.isPending ? "Creating..." : "Create Trip"}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setForm(initialForm)}>
                Clear Form
              </Button>
            </div>
          </form>
        </div>
      </AnimatedSection>
    </div>
  );
};

export default AddTripPage;
