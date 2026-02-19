import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createDriverCashHandover, getDriverCashSummary, listDriverCashHandovers } from "@/api/driverCashHandovers";
import { listDrivers } from "@/api/drivers";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { HandCoins } from "lucide-react";
import { toast } from "sonner";

const DriverCashPage = () => {
  const queryClient = useQueryClient();
  const [driverId, setDriverId] = useState("all");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [formDriverId, setFormDriverId] = useState("");
  const [formDate, setFormDate] = useState("");
  const [formAmount, setFormAmount] = useState("");
  const [formNotes, setFormNotes] = useState("");

  const drivers = useQuery({ queryKey: ["drivers"], queryFn: listDrivers });
  const handovers = useQuery({
    queryKey: ["driver-cash-handovers", driverId, startDate, endDate],
    queryFn: () =>
      listDriverCashHandovers({
        driverId: driverId === "all" ? undefined : Number(driverId),
        startDate: startDate || undefined,
        endDate: endDate || undefined,
      }),
  });
  const summary = useQuery({
    queryKey: ["driver-cash-summary", driverId, startDate, endDate],
    queryFn: () =>
      getDriverCashSummary({
        driverId: driverId === "all" ? undefined : Number(driverId),
        startDate: startDate || undefined,
        endDate: endDate || undefined,
      }),
  });

  const createMutation = useMutation({
    mutationFn: createDriverCashHandover,
    onSuccess: () => {
      toast.success("Driver cash handover saved.");
      setFormDate("");
      setFormAmount("");
      setFormNotes("");
      queryClient.invalidateQueries({ queryKey: ["driver-cash-handovers"] });
      queryClient.invalidateQueries({ queryKey: ["driver-cash-summary"] });
    },
    onError: () => toast.error("Failed to save handover."),
  });

  const totals = useMemo(() => {
    const rows = summary.data ?? [];
    const earned = rows.reduce((sum, row) => sum + Number(row.earned_amount_total), 0);
    const handover = rows.reduce((sum, row) => sum + Number(row.handover_amount_total), 0);
    const balance = rows.reduce((sum, row) => sum + Number(row.balance_amount), 0);
    return { earned, handover, balance };
  }, [summary.data]);

  return (
    <div className="space-y-5 max-w-7xl">
      <AnimatedSection>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
              <HandCoins size={22} />
            </div>
            <div>
              <h1 className="font-display text-3xl font-bold">Driver Cash Handover</h1>
              <p className="text-muted-foreground text-sm">Track driver advances and monthly remaining payable amount.</p>
            </div>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.05}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60 space-y-4">
          <h2 className="font-semibold text-lg">Add Cash Handover</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <Select value={formDriverId} onValueChange={setFormDriverId}>
              <SelectTrigger>
                <SelectValue placeholder="Select driver" />
              </SelectTrigger>
              <SelectContent>
                {(drivers.data ?? []).map((driver) => (
                  <SelectItem key={driver.id} value={String(driver.id)}>
                    {driver.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input type="date" value={formDate} onChange={(e) => setFormDate(e.target.value)} />
            <Input
              type="number"
              step="0.01"
              placeholder="Amount (AED)"
              value={formAmount}
              onChange={(e) => setFormAmount(e.target.value)}
            />
            <Input
              placeholder="Notes (optional)"
              value={formNotes}
              onChange={(e) => setFormNotes(e.target.value)}
            />
          </div>
          <Button
            onClick={() => {
              if (!formDriverId || !formDate || !formAmount) {
                toast.error("Please select driver, date, and amount.");
                return;
              }
              createMutation.mutate({
                driverId: Number(formDriverId),
                handoverDate: formDate,
                amount: Number(formAmount),
                notes: formNotes || undefined,
              });
            }}
            disabled={createMutation.isPending}
          >
            Save Handover
          </Button>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.1}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60 space-y-4">
          <h2 className="font-semibold text-lg">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Select value={driverId} onValueChange={setDriverId}>
              <SelectTrigger>
                <SelectValue placeholder="All drivers" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Drivers</SelectItem>
                {(drivers.data ?? []).map((driver) => (
                  <SelectItem key={driver.id} value={String(driver.id)}>
                    {driver.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.15}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <h2 className="font-semibold text-lg mb-3">Monthly Earn vs Cash Handover</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="text-xs px-2.5 py-1 rounded-full border border-border bg-muted/25">Earned: AED {totals.earned.toFixed(2)}</span>
            <span className="text-xs px-2.5 py-1 rounded-full border border-border bg-muted/25">Handover: AED {totals.handover.toFixed(2)}</span>
            <span className="text-xs px-2.5 py-1 rounded-full border border-border bg-muted/25">Left Payable: AED {totals.balance.toFixed(2)}</span>
          </div>

          {summary.isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-border/60 mb-4">
              <table className="w-full text-sm min-w-[860px]">
                <thead className="bg-muted/45">
                  <tr className="text-left">
                    <th className="px-3 py-3">Driver</th>
                    <th className="px-3 py-3">Trips</th>
                    <th className="px-3 py-3">Earned (AED)</th>
                    <th className="px-3 py-3">Handover (AED)</th>
                    <th className="px-3 py-3">Left Payable (AED)</th>
                  </tr>
                </thead>
                <tbody>
                  {(summary.data ?? []).map((row) => (
                    <tr key={row.driver_id} className="border-t border-border/60">
                      <td className="px-3 py-2">{row.driver_name}</td>
                      <td className="px-3 py-2">{row.trip_count}</td>
                      <td className="px-3 py-2">{Number(row.earned_amount_total).toFixed(2)}</td>
                      <td className="px-3 py-2">{Number(row.handover_amount_total).toFixed(2)}</td>
                      <td className="px-3 py-2 font-semibold">{Number(row.balance_amount).toFixed(2)}</td>
                    </tr>
                  ))}
                  {(summary.data ?? []).length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-3 py-8 text-center text-muted-foreground">
                        No summary data in selected range.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          <h2 className="font-semibold text-lg mb-3">Cash Handover Ledger</h2>
          {handovers.isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-border/60">
              <table className="w-full text-sm min-w-[860px]">
                <thead className="bg-muted/45">
                  <tr className="text-left">
                    <th className="px-3 py-3">Date</th>
                    <th className="px-3 py-3">Driver</th>
                    <th className="px-3 py-3">Amount (AED)</th>
                    <th className="px-3 py-3">Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {(handovers.data ?? []).map((row) => (
                    <tr key={row.id} className="border-t border-border/60">
                      <td className="px-3 py-2">{row.handover_date}</td>
                      <td className="px-3 py-2">{row.driver_name}</td>
                      <td className="px-3 py-2 font-semibold">{Number(row.amount).toFixed(2)}</td>
                      <td className="px-3 py-2">{row.notes || "-"}</td>
                    </tr>
                  ))}
                  {(handovers.data ?? []).length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                        No cash handover records in selected range.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </AnimatedSection>
    </div>
  );
};

export default DriverCashPage;
