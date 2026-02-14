import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listQuoteRequests, updateQuoteRequestStatus } from "@/api/publicApi";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { CheckCircle2, XCircle, MessageSquareText, Inbox, Search } from "lucide-react";

type StatusFilter = "all" | "pending" | "resolved" | "dismissed";

const statusClass: Record<string, string> = {
  resolved: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  dismissed: "bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300",
  pending: "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
};

const QuoteRequestsPage = () => {
  const qc = useQueryClient();
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<StatusFilter>("all");

  const requests = useQuery({ queryKey: ["quote-requests"], queryFn: listQuoteRequests });

  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => updateQuoteRequestStatus(id, status),
    onSuccess: () => {
      toast.success("Status updated!");
      qc.invalidateQueries({ queryKey: ["quote-requests"] });
    },
    onError: () => toast.error("Failed to update status."),
  });

  const filteredRequests = useMemo(() => {
    const list = requests.data ?? [];
    const q = query.trim().toLowerCase();

    return list.filter((req) => {
      const statusMatch = status === "all" ? true : req.status === status;
      const searchMatch = q
        ? `${req.name} ${req.email} ${req.mobile} ${req.freight} ${req.origin} ${req.destination} ${req.note ?? ""}`
            .toLowerCase()
            .includes(q)
        : true;
      return statusMatch && searchMatch;
    });
  }, [requests.data, query, status]);

  return (
    <div className="space-y-5">
      <AnimatedSection>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-violet-100 text-violet-700 dark:bg-violet-950/40 dark:text-violet-300 flex items-center justify-center">
              <MessageSquareText size={22} />
            </div>
            <div>
              <h1 className="font-display text-3xl font-bold">Quote Requests</h1>
              <p className="text-muted-foreground text-sm">{filteredRequests.length} requests shown</p>
            </div>
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
            <div className="w-full md:w-48">
              <Select value={status} onValueChange={(v) => setStatus(v as StatusFilter)}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
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
              {filteredRequests.map((req, idx) => (
                <motion.div
                  key={req.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: idx * 0.02 }}
                  className="border border-border/60 rounded-xl p-4 bg-background/50"
                >
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-semibold text-lg leading-none">{req.name}</h3>
                        <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${statusClass[req.status] ?? "bg-muted text-muted-foreground"}`}>
                          {req.status}
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

                    {req.status === "pending" && (
                      <div className="flex flex-wrap gap-2 shrink-0">
                        <Button size="sm" variant="outline" onClick={() => updateStatus.mutate({ id: req.id, status: "resolved" })}>
                          <CheckCircle2 size={14} className="mr-1" /> Resolve
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => updateStatus.mutate({ id: req.id, status: "dismissed" })}>
                          <XCircle size={14} className="mr-1" /> Dismiss
                        </Button>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
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
