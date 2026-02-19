import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createTrip } from "@/api/trips";
import { listCompanies } from "@/api/companies";
import { listDrivers } from "@/api/drivers";
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
  destinationCompanyName: "",
  tripCategory: "domestic",
  amount: "",
  tollGate: "",
  driverMode: "registered",
  driverId: "",
  otherDriverName: "",
  otherDriverMobile: "",
};

const freightOptions = ["1 - Ton", "3 - Ton", "7 - Ton", "10 - Ton", "Truck"];

const AddTripPage = () => {
  const qc = useQueryClient();
  const companies = useQuery({ queryKey: ["companies"], queryFn: listCompanies });
  const drivers = useQuery({ queryKey: ["drivers"], queryFn: listDrivers });
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
    if (form.driverMode === "registered" && !form.driverId) {
      toast.error("Please select a registered driver.");
      return;
    }
    if (form.driverMode === "other" && !form.otherDriverName.trim()) {
      toast.error("Please enter other driver name.");
      return;
    }
    mutation.mutate({
      companyId: Number(form.companyId),
      date: form.date,
      freight: form.freight,
      origin: form.origin,
      destination: form.destination,
      destinationCompanyName: form.destinationCompanyName || undefined,
      tripCategory: form.tripCategory as "domestic" | "international",
      amount: Number(form.amount),
      tollGate: Number(form.tollGate),
      driver:
        form.driverMode === "registered"
          ? drivers.data?.find((d) => String(d.id) === form.driverId)?.name || ""
          : form.otherDriverName,
      driverId: form.driverMode === "registered" && form.driverId ? Number(form.driverId) : undefined,
      externalDriverName: form.driverMode === "other" ? form.otherDriverName : undefined,
      externalDriverMobile: form.driverMode === "other" ? form.otherDriverMobile : undefined,
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
              <div className="h-full bg-accent-gradient transition-all" style={{ width: `${(completed / 11) * 100}%` }} />
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
                <Select value={form.freight} onValueChange={(v) => setForm({ ...form, freight: v })}>
                  <SelectTrigger className={fieldClass}>
                    <SelectValue placeholder="Select freight type" />
                  </SelectTrigger>
                  <SelectContent>
                    {freightOptions.map((item) => (
                      <SelectItem key={item} value={item}>
                        {item}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-semibold mb-2 block">Trip Category *</label>
                <Select
                  value={form.tripCategory}
                  onValueChange={(v) => setForm({ ...form, tripCategory: v as "domestic" | "international" })}
                >
                  <SelectTrigger className={fieldClass}>
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="domestic">Domestic (with VAT)</SelectItem>
                    <SelectItem value="international">International (without VAT)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><MapPin size={15} className="text-accent" /> Origin *</label>
                <Input className={fieldClass} value={form.origin} onChange={(e) => setForm({ ...form, origin: e.target.value })} placeholder="Pickup city" required />
              </div>
              <div>
                <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Navigation size={15} className="text-accent" /> Destination *</label>
                <Input className={fieldClass} value={form.destination} onChange={(e) => setForm({ ...form, destination: e.target.value })} placeholder="Delivery city" required />
              </div>
              <div className="md:col-span-2">
                <label className="text-sm font-semibold mb-2 block">Destination Company Name (Optional)</label>
                <Input
                  className={fieldClass}
                  value={form.destinationCompanyName}
                  onChange={(e) => setForm({ ...form, destinationCompanyName: e.target.value })}
                  placeholder="Destination company name"
                />
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
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <Select
                    value={form.driverMode}
                    onValueChange={(v) => setForm({ ...form, driverMode: v, driverId: "", otherDriverName: "", otherDriverMobile: "" })}
                  >
                    <SelectTrigger className={fieldClass}>
                      <SelectValue placeholder="Driver type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="registered">Registered Driver</SelectItem>
                      <SelectItem value="other">Other Driver</SelectItem>
                    </SelectContent>
                  </Select>

                  {form.driverMode === "registered" ? (
                    <div className="md:col-span-2">
                      <Select value={form.driverId} onValueChange={(v) => setForm({ ...form, driverId: v })}>
                        <SelectTrigger className={fieldClass}>
                          <SelectValue placeholder="Select registered driver" />
                        </SelectTrigger>
                        <SelectContent>
                          {drivers.data?.map((d) => (
                            <SelectItem key={d.id} value={String(d.id)}>
                              {d.name} ({d.mobile_number})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  ) : (
                    <>
                      <Input
                        className={fieldClass}
                        value={form.otherDriverName}
                        onChange={(e) => setForm({ ...form, otherDriverName: e.target.value })}
                        placeholder="Other driver name"
                        required={form.driverMode === "other"}
                      />
                      <Input
                        className={fieldClass}
                        value={form.otherDriverMobile}
                        onChange={(e) => setForm({ ...form, otherDriverMobile: e.target.value })}
                        placeholder="Other driver mobile"
                      />
                    </>
                  )}
                </div>
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
