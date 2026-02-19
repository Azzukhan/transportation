import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createDriver, listDrivers } from "@/api/drivers";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle, Plus, Users } from "lucide-react";
import { toast } from "sonner";

const initialForm = {
  name: "",
  mobileNumber: "",
  passportNumber: "",
  emiratesIdNumber: "",
  emiratesIdExpiryDate: "",
};

const DriversPage = () => {
  const qc = useQueryClient();
  const [form, setForm] = useState(initialForm);
  const [expiryInputType, setExpiryInputType] = useState<"text" | "date">("text");
  const drivers = useQuery({ queryKey: ["drivers"], queryFn: listDrivers });

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const expiringSoon = (drivers.data ?? [])
    .map((driver) => {
      if (!driver.emirates_id_expiry_date) return null;
      const expiry = new Date(driver.emirates_id_expiry_date);
      expiry.setHours(0, 0, 0, 0);
      const daysLeft = Math.ceil((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
      if (daysLeft > 30) return null;
      return { id: driver.id, name: driver.name, daysLeft };
    })
    .filter((item): item is { id: number; name: string; daysLeft: number } => item !== null);

  const create = useMutation({
    mutationFn: createDriver,
    onSuccess: () => {
      toast.success("Driver added.");
      setForm(initialForm);
      qc.invalidateQueries({ queryKey: ["drivers"] });
    },
    onError: () => toast.error("Failed to add driver."),
  });

  return (
    <div className="space-y-5 max-w-6xl">
      <AnimatedSection>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-sky-100 text-sky-700 dark:bg-sky-950/40 dark:text-sky-300 flex items-center justify-center">
              <Users size={22} />
            </div>
            <div>
              <h1 className="font-display text-3xl font-bold">Driver Details</h1>
              <p className="text-muted-foreground text-sm">Register and manage driver information.</p>
            </div>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.05}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60 space-y-4">
          <h2 className="font-semibold text-lg">Add New Driver</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <Input placeholder="Driver name *" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <Input placeholder="Mobile number *" value={form.mobileNumber} onChange={(e) => setForm({ ...form, mobileNumber: e.target.value })} />
            <Input placeholder="Passport number" value={form.passportNumber} onChange={(e) => setForm({ ...form, passportNumber: e.target.value })} />
            <Input placeholder="Emirates ID number" value={form.emiratesIdNumber} onChange={(e) => setForm({ ...form, emiratesIdNumber: e.target.value })} />
            <Input
              type={expiryInputType}
              placeholder="Emirates ID Expiry Date"
              value={form.emiratesIdExpiryDate}
              onFocus={() => setExpiryInputType("date")}
              onBlur={() => {
                if (!form.emiratesIdExpiryDate) setExpiryInputType("text");
              }}
              onChange={(e) => setForm({ ...form, emiratesIdExpiryDate: e.target.value })}
            />
          </div>
          <Button
            onClick={() => {
              if (!form.name.trim() || !form.mobileNumber.trim()) {
                toast.error("Name and mobile number are required.");
                return;
              }
              create.mutate({
                name: form.name.trim(),
                mobileNumber: form.mobileNumber.trim(),
                passportNumber: form.passportNumber.trim() || undefined,
                emiratesIdNumber: form.emiratesIdNumber.trim() || undefined,
                emiratesIdExpiryDate: form.emiratesIdExpiryDate || undefined,
              });
            }}
            className="bg-accent-gradient text-accent-foreground border-0"
            disabled={create.isPending}
          >
            <Plus size={15} className="mr-1.5" /> {create.isPending ? "Adding..." : "Add Driver"}
          </Button>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.1}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          {expiringSoon.length > 0 && (
            <div className="mb-4 rounded-xl border border-amber-300/70 bg-amber-50 p-4">
              <div className="flex items-center gap-2 text-amber-800 mb-2">
                <AlertTriangle size={16} />
                <p className="text-sm font-semibold">Emirates ID / Visa Expiry Alert</p>
              </div>
              <div className="space-y-1.5">
                {expiringSoon.map((item) => (
                  <p key={item.id} className="text-sm text-amber-900">
                    {item.name}: Emirates ID/visa{" "}
                    {item.daysLeft >= 0 ? `will expire in ${item.daysLeft} day(s)` : `expired ${Math.abs(item.daysLeft)} day(s) ago`} - please contact driver and apply renewal.
                  </p>
                ))}
              </div>
            </div>
          )}

          {drivers.isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-11 w-full rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-border/60">
              <table className="w-full text-sm">
                <thead className="bg-muted/45">
                  <tr className="text-left">
                    <th className="px-4 py-3 font-semibold text-muted-foreground">ID</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Name</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Mobile</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Passport</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Emirates ID</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">ID Expiry</th>
                  </tr>
                </thead>
                <tbody>
                  {(drivers.data ?? []).map((d) => (
                    <tr key={d.id} className="border-t border-border/60 hover:bg-muted/40 transition-colors">
                      <td className="px-4 py-3">#{d.id}</td>
                      <td className="px-4 py-3">{d.name}</td>
                      <td className="px-4 py-3">{d.mobile_number}</td>
                      <td className="px-4 py-3">{d.passport_number || "-"}</td>
                      <td className="px-4 py-3">{d.emirates_id_number || "-"}</td>
                      <td className="px-4 py-3">{d.emirates_id_expiry_date || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </AnimatedSection>
    </div>
  );
};

export default DriversPage;
