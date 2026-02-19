import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listQuoteRequests, updateQuoteRequest, updateQuoteRequestStatus } from "@/api/publicApi";
import { listCompanies, createCompany } from "@/api/companies";
import { createTrip } from "@/api/trips";
import { listDrivers } from "@/api/drivers";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { CheckCircle2, XCircle, MessageSquareText, Inbox, Search, PencilLine, Truck, Plus } from "lucide-react";

type StatusFilter = "all" | "pending" | "responded" | "accepted" | "dismissed";

const statusClass: Record<string, string> = {
  pending: "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  responded: "bg-sky-100 text-sky-700 dark:bg-sky-950/40 dark:text-sky-300",
  accepted: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  dismissed: "bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300",
};

type EditForm = {
  name: string;
  email: string;
  mobile: string;
  freight: string;
  origin: string;
  destination: string;
  note: string;
};

type ConvertForm = {
  mode: "existing" | "new";
  companyId: string;
  date: string;
  tripCategory: "domestic" | "international";
  amount: string;
  tollGate: string;
  destinationCompanyName: string;
  driverMode: "registered" | "other";
  driverId: string;
  otherDriverName: string;
  otherDriverMobile: string;
  newCompanyName: string;
  newCompanyAddress: string;
  newCompanyEmail: string;
  newCompanyPhone: string;
  newCompanyTrn: string;
  newContactPerson: string;
  newPoBox: string;
};

const initialConvertForm = (req: EditForm): ConvertForm => ({
  mode: "existing",
  companyId: "",
  date: new Date().toISOString().slice(0, 10),
  tripCategory: "domestic",
  amount: "",
  tollGate: "0",
  destinationCompanyName: "",
  driverMode: "registered",
  driverId: "",
  otherDriverName: "",
  otherDriverMobile: "",
  newCompanyName: req.name,
  newCompanyAddress: "Dubai, UAE",
  newCompanyEmail: req.email,
  newCompanyPhone: req.mobile,
  newCompanyTrn: "",
  newContactPerson: req.name,
  newPoBox: "N/A",
});

const QuoteRequestsPage = () => {
  const qc = useQueryClient();
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<StatusFilter>("all");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<EditForm | null>(null);
  const [convertId, setConvertId] = useState<number | null>(null);
  const [convertForm, setConvertForm] = useState<ConvertForm | null>(null);

  const requests = useQuery({ queryKey: ["quote-requests"], queryFn: listQuoteRequests });
  const companies = useQuery({ queryKey: ["companies"], queryFn: listCompanies });
  const drivers = useQuery({ queryKey: ["drivers"], queryFn: listDrivers });

  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => updateQuoteRequestStatus(id, status),
    onSuccess: () => {
      toast.success("Status updated!");
      qc.invalidateQueries({ queryKey: ["quote-requests"] });
    },
    onError: () => toast.error("Failed to update status."),
  });

  const saveEdit = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: EditForm }) => updateQuoteRequest(id, payload),
    onSuccess: () => {
      toast.success("Quote request updated.");
      setEditingId(null);
      setEditForm(null);
      qc.invalidateQueries({ queryKey: ["quote-requests"] });
    },
    onError: () => toast.error("Failed to update quote request."),
  });

  const addAsTrip = useMutation({
    mutationFn: async ({ reqId, req }: { reqId: number; req: EditForm }) => {
      if (!convertForm) throw new Error("Convert form missing");

      let companyId = Number(convertForm.companyId);

      if (convertForm.mode === "new") {
        const created = await createCompany({
          name: convertForm.newCompanyName,
          address: convertForm.newCompanyAddress,
          email: convertForm.newCompanyEmail,
          phone: convertForm.newCompanyPhone,
          trn: convertForm.newCompanyTrn,
          contactPerson: convertForm.newContactPerson,
          poBox: convertForm.newPoBox,
        });
        companyId = created.id;
      }

      await createTrip({
        companyId,
        date: convertForm.date,
        freight: req.freight,
        origin: req.origin,
        destination: req.destination,
        destinationCompanyName: convertForm.destinationCompanyName || undefined,
        tripCategory: convertForm.tripCategory,
        amount: Number(convertForm.amount),
        tollGate: Number(convertForm.tollGate || 0),
        driver:
          convertForm.driverMode === "registered"
            ? drivers.data?.find((d) => String(d.id) === convertForm.driverId)?.name || ""
            : convertForm.otherDriverName,
        driverId: convertForm.driverMode === "registered" && convertForm.driverId ? Number(convertForm.driverId) : undefined,
        externalDriverName: convertForm.driverMode === "other" ? convertForm.otherDriverName : undefined,
        externalDriverMobile: convertForm.driverMode === "other" ? convertForm.otherDriverMobile : undefined,
      });

      await updateQuoteRequestStatus(reqId, "accepted");
    },
    onSuccess: () => {
      toast.success("Trip created and quote marked as accepted.");
      setConvertId(null);
      setConvertForm(null);
      qc.invalidateQueries({ queryKey: ["quote-requests"] });
      qc.invalidateQueries({ queryKey: ["trips"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
    },
    onError: () => toast.error("Failed to convert quote to trip."),
  });

  const filteredRequests = useMemo(() => {
    const list = requests.data ?? [];
    const q = query.trim().toLowerCase();

    return list.filter((req) => {
      const normalizedStatus = req.status === "new" || !req.status ? "pending" : req.status;
      const statusMatch = status === "all" ? true : normalizedStatus === status;
      const searchMatch = q
        ? `${req.name} ${req.email} ${req.mobile} ${req.freight} ${req.origin} ${req.destination} ${req.note ?? ""}`
            .toLowerCase()
            .includes(q)
        : true;
      return statusMatch && searchMatch;
    });
  }, [requests.data, query, status]);

  const beginEdit = (req: EditForm & { id: number }) => {
    setEditingId(req.id);
    setEditForm({
      name: req.name,
      email: req.email,
      mobile: req.mobile,
      freight: req.freight,
      origin: req.origin,
      destination: req.destination,
      note: req.note,
    });
  };

  const beginConvert = (req: EditForm & { id: number }) => {
    setConvertId(req.id);
    setConvertForm(initialConvertForm(req));
  };

  return (
    <div className="space-y-5">
      <AnimatedSection>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-violet-100 text-violet-700 dark:bg-violet-950/40 dark:text-violet-300 flex items-center justify-center">
                <MessageSquareText size={22} />
              </div>
              <div>
                <h1 className="font-display text-3xl font-bold">Quote Requests</h1>
                <p className="text-muted-foreground text-sm">{filteredRequests.length} requests shown</p>
              </div>
            </div>
            <Button asChild className="bg-accent-gradient text-accent-foreground border-0">
              <Link to="/create-quote">
                <Plus size={15} className="mr-1" /> Generate Quotation
              </Link>
            </Button>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.08}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60 space-y-4">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search by client, route, or freight"
                className="pl-9"
              />
            </div>
            <div className="w-full md:w-52">
              <Select value={status} onValueChange={(v) => setStatus(v as StatusFilter)}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="responded">Responded</SelectItem>
                  <SelectItem value="accepted">Accepted</SelectItem>
                  <SelectItem value="dismissed">Dismissed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {requests.isLoading ? (
            <div className="space-y-3 py-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="border border-border/60 rounded-xl p-4 space-y-2">
                  <Skeleton className="h-4 w-1/3" />
                  <Skeleton className="h-3 w-1/2" />
                  <Skeleton className="h-3 w-2/3" />
                  <Skeleton className="h-3 w-full" />
                </div>
              ))}
            </div>
          ) : filteredRequests.length > 0 ? (
            <div className="space-y-3">
              {filteredRequests.map((req, idx) => {
                const reqStatus = req.status === "new" || !req.status ? "pending" : req.status;
                const isEditing = editingId === req.id && editForm;
                const isConverting = convertId === req.id && convertForm;

                return (
                  <motion.div
                    key={req.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2, delay: idx * 0.02 }}
                    className="border border-border/60 rounded-xl p-4 bg-background/50"
                  >
                    <div className="space-y-3">
                      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                        <div className="space-y-2 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="font-semibold text-lg leading-none">{req.name}</h3>
                            <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${statusClass[reqStatus] ?? "bg-muted text-muted-foreground"}`}>
                              {reqStatus}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">{req.email} - {req.mobile}</p>
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm">
                            <div><span className="text-muted-foreground">Freight:</span> {req.freight}</div>
                            <div><span className="text-muted-foreground">Origin:</span> {req.origin}</div>
                            <div><span className="text-muted-foreground">Destination:</span> {req.destination}</div>
                          </div>
                          {req.note && <p className="text-sm text-muted-foreground italic">"{req.note}"</p>}
                        </div>

                        <div className="flex flex-wrap gap-2 shrink-0">
                          {(reqStatus === "pending" || reqStatus === "responded") && (
                            <Button size="sm" variant="outline" onClick={() => updateStatus.mutate({ id: req.id, status: "responded" })}>
                              <CheckCircle2 size={14} className="mr-1" /> Mark Responded
                            </Button>
                          )}
                          {(reqStatus === "pending" || reqStatus === "responded") && (
                            <Button size="sm" variant="outline" onClick={() => beginEdit({ ...req, note: req.note ?? "" })}>
                              <PencilLine size={14} className="mr-1" /> Edit
                            </Button>
                          )}
                          {reqStatus === "accepted" && (
                            <Button size="sm" variant="outline" onClick={() => beginConvert({ ...req, note: req.note ?? "" })}>
                              <Truck size={14} className="mr-1" /> Add as Trip
                            </Button>
                          )}
                          {(reqStatus === "pending" || reqStatus === "responded") && (
                            <Button size="sm" variant="outline" onClick={() => updateStatus.mutate({ id: req.id, status: "accepted" })}>
                              <CheckCircle2 size={14} className="mr-1" /> Accept
                            </Button>
                          )}
                          {(reqStatus === "pending" || reqStatus === "responded") && (
                            <Button size="sm" variant="outline" onClick={() => updateStatus.mutate({ id: req.id, status: "dismissed" })}>
                              <XCircle size={14} className="mr-1" /> Dismiss
                            </Button>
                          )}
                        </div>
                      </div>

                      {isEditing && editForm && (
                        <div className="rounded-lg border border-border/60 bg-card p-4 space-y-3">
                          <p className="text-sm font-semibold">Edit Quote Request</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <Input value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} placeholder="Name" />
                            <Input value={editForm.email} onChange={(e) => setEditForm({ ...editForm, email: e.target.value })} placeholder="Email" />
                            <Input value={editForm.mobile} onChange={(e) => setEditForm({ ...editForm, mobile: e.target.value })} placeholder="Mobile" />
                            <Input value={editForm.freight} onChange={(e) => setEditForm({ ...editForm, freight: e.target.value })} placeholder="Freight" />
                            <Input value={editForm.origin} onChange={(e) => setEditForm({ ...editForm, origin: e.target.value })} placeholder="Origin" />
                            <Input value={editForm.destination} onChange={(e) => setEditForm({ ...editForm, destination: e.target.value })} placeholder="Destination" />
                          </div>
                          <Input value={editForm.note} onChange={(e) => setEditForm({ ...editForm, note: e.target.value })} placeholder="Note" />
                          <div className="flex gap-2">
                            <Button size="sm" onClick={() => saveEdit.mutate({ id: req.id, payload: editForm })} disabled={saveEdit.isPending}>Save</Button>
                            <Button size="sm" variant="ghost" onClick={() => { setEditingId(null); setEditForm(null); }}>Cancel</Button>
                          </div>
                        </div>
                      )}

                      {isConverting && convertForm && (
                        <div className="rounded-lg border border-border/60 bg-card p-4 space-y-3">
                          <p className="text-sm font-semibold">Convert to Trip</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                              <label className="text-xs text-muted-foreground">Customer Type</label>
                              <Select value={convertForm.mode} onValueChange={(v) => setConvertForm({ ...convertForm, mode: v as "existing" | "new" })}>
                                <SelectTrigger><SelectValue /></SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="existing">Existing Company</SelectItem>
                                  <SelectItem value="new">New Customer</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>

                            {convertForm.mode === "existing" ? (
                              <div>
                                <label className="text-xs text-muted-foreground">Company</label>
                                <Select value={convertForm.companyId} onValueChange={(v) => setConvertForm({ ...convertForm, companyId: v })}>
                                  <SelectTrigger><SelectValue placeholder="Select company" /></SelectTrigger>
                                  <SelectContent>
                                    {companies.data?.map((c) => (
                                      <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                            ) : (
                              <>
                                <Input value={convertForm.newCompanyName} onChange={(e) => setConvertForm({ ...convertForm, newCompanyName: e.target.value })} placeholder="New company name" />
                                <Input value={convertForm.newCompanyEmail} onChange={(e) => setConvertForm({ ...convertForm, newCompanyEmail: e.target.value })} placeholder="New company email" />
                                <Input value={convertForm.newCompanyPhone} onChange={(e) => setConvertForm({ ...convertForm, newCompanyPhone: e.target.value })} placeholder="Phone" />
                                <Input value={convertForm.newCompanyTrn} onChange={(e) => setConvertForm({ ...convertForm, newCompanyTrn: e.target.value })} placeholder="TRN" />
                                <Input value={convertForm.newCompanyAddress} onChange={(e) => setConvertForm({ ...convertForm, newCompanyAddress: e.target.value })} placeholder="Address" />
                                <Input value={convertForm.newContactPerson} onChange={(e) => setConvertForm({ ...convertForm, newContactPerson: e.target.value })} placeholder="Contact person" />
                                <Input value={convertForm.newPoBox} onChange={(e) => setConvertForm({ ...convertForm, newPoBox: e.target.value })} placeholder="PO Box" />
                              </>
                            )}

                            <Input type="date" value={convertForm.date} onChange={(e) => setConvertForm({ ...convertForm, date: e.target.value })} />
                            <Select
                              value={convertForm.tripCategory}
                              onValueChange={(v) => setConvertForm({ ...convertForm, tripCategory: v as "domestic" | "international" })}
                            >
                              <SelectTrigger><SelectValue placeholder="Trip category" /></SelectTrigger>
                              <SelectContent>
                                <SelectItem value="domestic">Domestic (with VAT)</SelectItem>
                                <SelectItem value="international">International (without VAT)</SelectItem>
                              </SelectContent>
                            </Select>
                            <Input
                              value={convertForm.destinationCompanyName}
                              onChange={(e) => setConvertForm({ ...convertForm, destinationCompanyName: e.target.value })}
                              placeholder="Destination company name (optional)"
                            />
                            <Select
                              value={convertForm.driverMode}
                              onValueChange={(v) =>
                                setConvertForm({
                                  ...convertForm,
                                  driverMode: v as "registered" | "other",
                                  driverId: "",
                                  otherDriverName: "",
                                  otherDriverMobile: "",
                                })
                              }
                            >
                              <SelectTrigger><SelectValue placeholder="Driver type" /></SelectTrigger>
                              <SelectContent>
                                <SelectItem value="registered">Registered Driver</SelectItem>
                                <SelectItem value="other">Other Driver</SelectItem>
                              </SelectContent>
                            </Select>
                            {convertForm.driverMode === "registered" ? (
                              <Select
                                value={convertForm.driverId}
                                onValueChange={(v) => setConvertForm({ ...convertForm, driverId: v })}
                              >
                                <SelectTrigger><SelectValue placeholder="Select driver" /></SelectTrigger>
                                <SelectContent>
                                  {drivers.data?.map((driver) => (
                                    <SelectItem key={driver.id} value={String(driver.id)}>
                                      {driver.name} ({driver.mobile_number})
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            ) : (
                              <>
                                <Input
                                  value={convertForm.otherDriverName}
                                  onChange={(e) => setConvertForm({ ...convertForm, otherDriverName: e.target.value })}
                                  placeholder="Other driver name"
                                />
                                <Input
                                  value={convertForm.otherDriverMobile}
                                  onChange={(e) => setConvertForm({ ...convertForm, otherDriverMobile: e.target.value })}
                                  placeholder="Other driver mobile"
                                />
                              </>
                            )}
                            <Input type="number" value={convertForm.amount} onChange={(e) => setConvertForm({ ...convertForm, amount: e.target.value })} placeholder="Amount (AED)" />
                            <Input type="number" value={convertForm.tollGate} onChange={(e) => setConvertForm({ ...convertForm, tollGate: e.target.value })} placeholder="Toll Gate (AED)" />
                          </div>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              onClick={() => {
                                if (!convertForm.date || !convertForm.amount) {
                                  toast.error("Please fill trip date and amount.");
                                  return;
                                }
                                if (convertForm.driverMode === "registered" && !convertForm.driverId) {
                                  toast.error("Please select a registered driver.");
                                  return;
                                }
                                if (convertForm.driverMode === "other" && !convertForm.otherDriverName.trim()) {
                                  toast.error("Please fill other driver name.");
                                  return;
                                }
                                if (convertForm.mode === "existing" && !convertForm.companyId) {
                                  toast.error("Please select an existing company.");
                                  return;
                                }
                                if (
                                  convertForm.mode === "new" &&
                                  (
                                    !convertForm.newCompanyName ||
                                    !convertForm.newCompanyEmail ||
                                    !convertForm.newCompanyPhone ||
                                    !convertForm.newCompanyTrn ||
                                    !convertForm.newCompanyAddress
                                  )
                                ) {
                                  toast.error("Please fill new customer details.");
                                  return;
                                }
                                addAsTrip.mutate({ reqId: req.id, req: { ...req, note: req.note ?? "" } });
                              }}
                              disabled={addAsTrip.isPending}
                            >
                              {addAsTrip.isPending ? "Converting..." : "Create Trip + Accept"}
                            </Button>
                            <Button size="sm" variant="ghost" onClick={() => { setConvertId(null); setConvertForm(null); }}>Cancel</Button>
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-16 text-center bg-muted/20">
              <Inbox size={42} className="mx-auto text-muted-foreground/60 mb-4" />
              <p className="font-semibold text-lg">No quote requests found.</p>
              <p className="text-sm text-muted-foreground mt-1">Try adjusting your search or status filters.</p>
            </div>
          )}
        </div>
      </AnimatedSection>
    </div>
  );
};

export default QuoteRequestsPage;
