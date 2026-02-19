import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createInvoice, downloadSignatorySignature, listSignatories } from "@/api/invoices";
import { listCompanies } from "@/api/companies";
import { listTrips } from "@/api/trips";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { FileText, CalendarRange, Building2, Signature } from "lucide-react";

const CreateInvoicePage = () => {
  const qc = useQueryClient();
  const [companyId, setCompanyId] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [invoiceNumber, setInvoiceNumber] = useState("");
  const [preparedByMode, setPreparedByMode] = useState<"without_signature" | "with_signature">("without_signature");
  const [signatoryId, setSignatoryId] = useState("");
  const [signatoryPreviewUrl, setSignatoryPreviewUrl] = useState<string | null>(null);
  const [formatKey, setFormatKey] = useState("standard");
  const [selectedTripIds, setSelectedTripIds] = useState<number[]>([]);

  const companies = useQuery({ queryKey: ["companies"], queryFn: listCompanies });
  const signatories = useQuery({ queryKey: ["signatories"], queryFn: listSignatories });
  const companyNumericId = companyId ? Number(companyId) : undefined;
  const selectedSignatory = useMemo(
    () => signatories.data?.find((item) => String(item.id) === signatoryId),
    [signatories.data, signatoryId],
  );

  useEffect(() => {
    let canceled = false;
    let urlToRevoke: string | null = null;
    const load = async () => {
      if (preparedByMode !== "with_signature" || !signatoryId || !selectedSignatory?.has_signature) {
        setSignatoryPreviewUrl(null);
        return;
      }
      try {
        const { blob } = await downloadSignatorySignature(Number(signatoryId));
        const url = URL.createObjectURL(blob);
        if (canceled) {
          URL.revokeObjectURL(url);
          return;
        }
        urlToRevoke = url;
        setSignatoryPreviewUrl(url);
      } catch {
        if (!canceled) setSignatoryPreviewUrl(null);
      }
    };
    void load();
    return () => {
      canceled = true;
      if (urlToRevoke) URL.revokeObjectURL(urlToRevoke);
    };
  }, [preparedByMode, selectedSignatory?.has_signature, signatoryId]);

  const trips = useQuery({
    queryKey: ["trips", companyNumericId],
    queryFn: () => listTrips({ companyId: companyNumericId }),
    enabled: Boolean(companyNumericId),
  });

  const unpaidTrips = useMemo(
    () => (trips.data ?? []).filter((trip) => !trip.paid),
    [trips.data],
  );

  const visibleTrips = useMemo(() => {
    return unpaidTrips.filter((trip) => {
      if (fromDate && trip.date < fromDate) return false;
      if (toDate && trip.date > toDate) return false;
      return true;
    });
  }, [unpaidTrips, fromDate, toDate]);

  const selectedTrips = useMemo(
    () => unpaidTrips.filter((trip) => selectedTripIds.includes(trip.id)),
    [unpaidTrips, selectedTripIds],
  );

  const selectedTotal = useMemo(
    () => selectedTrips.reduce((sum, trip) => sum + Number(trip.total_amount ?? 0), 0),
    [selectedTrips],
  );

  const mutation = useMutation({
    mutationFn: createInvoice,
    onSuccess: () => {
      toast.success("Invoice created successfully!");
      qc.invalidateQueries({ queryKey: ["invoices"] });
      qc.invalidateQueries({ queryKey: ["trips"] });
      setSelectedTripIds([]);
      setFromDate("");
      setToDate("");
      setDueDate("");
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : "Failed to create invoice.";
      toast.error(message);
    },
  });

  const allVisibleSelected = visibleTrips.length > 0 && visibleTrips.every((trip) => selectedTripIds.includes(trip.id));

  const toggleTrip = (tripId: number, checked: boolean) => {
    setSelectedTripIds((prev) =>
      checked ? (prev.includes(tripId) ? prev : [...prev, tripId]) : prev.filter((id) => id !== tripId),
    );
  };

  const toggleAllVisible = (checked: boolean) => {
    if (!checked) {
      const visibleSet = new Set(visibleTrips.map((trip) => trip.id));
      setSelectedTripIds((prev) => prev.filter((id) => !visibleSet.has(id)));
      return;
    }
    setSelectedTripIds((prev) => Array.from(new Set([...prev, ...visibleTrips.map((trip) => trip.id)])));
  };

  const handleCreateInvoice = () => {
    if (!companyNumericId) {
      toast.error("Please select a company.");
      return;
    }
    if (selectedTripIds.length === 0) {
      toast.error("Please select at least one trip.");
      return;
    }
    if (preparedByMode === "with_signature" && !signatoryId) {
      toast.error("Please select a signatory.");
      return;
    }

    mutation.mutate({
      companyId: companyNumericId,
      dueDate: dueDate || undefined,
      invoiceNumber: invoiceNumber.trim() || undefined,
      preparedByMode,
      signatoryId: preparedByMode === "with_signature" && signatoryId ? Number(signatoryId) : undefined,
      formatKey,
      tripIds: selectedTripIds,
      startDate: fromDate || undefined,
      endDate: toDate || undefined,
    });
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 rounded-2xl bg-accent/15 border border-accent/25 flex items-center justify-center">
            <FileText size={26} className="text-accent" />
          </div>
          <div>
            <h1 className="font-display text-4xl font-bold">Create Invoice</h1>
            <p className="text-muted-foreground">Select company and choose exact trips to include.</p>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.08}>
        <div className="bg-card rounded-2xl p-6 md:p-8 shadow-elevated border border-border/60 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="lg:col-span-2">
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Building2 size={15} className="text-accent" /> Company *</label>
              <Select
                value={companyId}
                onValueChange={(value) => {
                  setCompanyId(value);
                  setSelectedTripIds([]);
                  setFromDate("");
                  setToDate("");
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select company" />
                </SelectTrigger>
                <SelectContent>
                  {companies.data?.map((company) => (
                    <SelectItem key={company.id} value={String(company.id)}>{company.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block">From</label>
              <Input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block">To</label>
              <Input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block">Due Date</label>
              <Input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block">Invoice Number</label>
              <Input
                type="text"
                value={invoiceNumber}
                onChange={(e) => setInvoiceNumber(e.target.value)}
                placeholder="Optional custom invoice no."
              />
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block">Template</label>
              <Select value={formatKey} onValueChange={setFormatKey}>
                <SelectTrigger>
                  <SelectValue placeholder="Template" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="standard">Standard</SelectItem>
                  <SelectItem value="template_c">Detailed Multi-Page</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block flex items-center gap-2"><Signature size={15} className="text-accent" /> Prepare By</label>
              <Select
                value={preparedByMode}
                onValueChange={(value: "without_signature" | "with_signature") => {
                  setPreparedByMode(value);
                  if (value === "without_signature") {
                    setSignatoryId("");
                  }
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select mode" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="without_signature">Without Signature</SelectItem>
                  <SelectItem value="with_signature">With Signature</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-semibold mb-2 block">Signature</label>
              <Select
                value={signatoryId}
                onValueChange={setSignatoryId}
                disabled={preparedByMode !== "with_signature"}
              >
                <SelectTrigger>
                  <SelectValue placeholder={preparedByMode === "with_signature" ? "Select signatory" : "Enable with signature first"} />
                </SelectTrigger>
                <SelectContent>
                  {signatories.data?.map((signatory) => (
                    <SelectItem key={signatory.id} value={String(signatory.id)}>
                      {signatory.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {preparedByMode === "with_signature" ? (
                signatoryPreviewUrl ? (
                  <div className="mt-2 rounded-lg border border-border/60 bg-muted/20 p-2.5">
                    <p className="text-xs text-muted-foreground mb-1">Selected signature preview</p>
                    <img
                      src={signatoryPreviewUrl}
                      alt={`${selectedSignatory?.name ?? "Signatory"} signature`}
                      className="h-14 w-full max-w-[220px] rounded bg-white object-contain border border-border/60"
                    />
                  </div>
                ) : signatoryId ? (
                  <p className="mt-2 text-xs text-muted-foreground">No signature image found for selected signatory.</p>
                ) : null
              ) : null}
            </div>
          </div>

          <div className="rounded-xl border border-border/60 overflow-hidden">
            <div className="bg-muted/40 px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Checkbox
                  checked={allVisibleSelected}
                  onCheckedChange={(v) => toggleAllVisible(v === true)}
                  disabled={visibleTrips.length === 0}
                />
                <span className="text-sm font-semibold">Select Visible Trips</span>
              </div>
              <span className="text-xs text-muted-foreground">{selectedTripIds.length} selected</span>
            </div>

            <div className="max-h-[420px] overflow-auto">
              {trips.isLoading ? (
                <p className="p-4 text-sm text-muted-foreground">Loading trips...</p>
              ) : visibleTrips.length > 0 ? (
                <table className="w-full text-sm">
                  <thead className="bg-muted/20 sticky top-0">
                    <tr className="text-left">
                      <th className="px-4 py-2.5">Pick</th>
                      <th className="px-4 py-2.5">Date</th>
                      <th className="px-4 py-2.5">Freight</th>
                      <th className="px-4 py-2.5">Route</th>
                      <th className="px-4 py-2.5 text-right">Total (AED)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleTrips.map((trip) => (
                      <tr key={trip.id} className="border-t border-border/60 hover:bg-muted/20">
                        <td className="px-4 py-3">
                          <Checkbox
                            checked={selectedTripIds.includes(trip.id)}
                            onCheckedChange={(v) => toggleTrip(trip.id, v === true)}
                          />
                        </td>
                        <td className="px-4 py-3">{trip.date}</td>
                        <td className="px-4 py-3">{trip.freight}</td>
                        <td className="px-4 py-3">{trip.origin} - {trip.destination}</td>
                        <td className="px-4 py-3 text-right font-semibold">AED {Number(trip.total_amount).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="p-4 text-sm text-muted-foreground">No unpaid trips available for selected filters.</p>
              )}
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-muted/30 border border-border/50">
            <div>
              <p className="text-sm text-muted-foreground">Selected Trips</p>
              <p className="font-display text-2xl font-bold">{selectedTripIds.length}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Estimated Invoice Total</p>
              <p className="font-display text-2xl font-bold text-accent">AED {selectedTotal.toFixed(2)}</p>
            </div>
            <Button
              onClick={handleCreateInvoice}
              disabled={mutation.isPending || selectedTripIds.length === 0}
              className="bg-accent-gradient text-accent-foreground border-0"
            >
              {mutation.isPending ? "Creating Invoice..." : "Create Invoice"}
            </Button>
          </div>

          <p className="text-xs text-muted-foreground flex items-center gap-1">
            <CalendarRange size={13} /> You can either filter by date range or select trips one-by-one.
          </p>
        </div>
      </AnimatedSection>
    </div>
  );
};

export default CreateInvoicePage;
