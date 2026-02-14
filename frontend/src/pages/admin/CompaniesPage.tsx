import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listInvoices, markInvoicePaid, downloadInvoicePdf } from "@/api/invoices";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { CheckCircle2, Download, Receipt, CircleAlert, Search } from "lucide-react";

interface CompaniesPageProps {
  status: "paid" | "unpaid";
}

type SortMode = "due_desc" | "due_asc" | "amount_desc" | "amount_asc";

const CompaniesPage = ({ status }: CompaniesPageProps) => {
  const qc = useQueryClient();
  const [query, setQuery] = useState("");
  const [sortBy, setSortBy] = useState<SortMode>("due_desc");

  const invoices = useQuery({
    queryKey: ["invoices", status],
    queryFn: () => listInvoices(status),
  });

  const markPaid = useMutation({
    mutationFn: markInvoicePaid,
    onSuccess: () => {
      toast.success("Invoice marked as paid!");
      qc.invalidateQueries({ queryKey: ["invoices"] });
    },
    onError: () => toast.error("Failed to update invoice."),
  });

  const handleDownloadPdf = async (invoiceId: number) => {
    try {
      const blob = await downloadInvoicePdf(invoiceId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `invoice-${invoiceId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Failed to download PDF.");
    }
  };

  const filteredInvoices = useMemo(() => {
    const list = invoices.data ?? [];
    const q = query.trim().toLowerCase();
    const searched = q
      ? list.filter((inv) => {
          const hay = `${inv.id} ${inv.company_name ?? ""} ${inv.start_date} ${inv.end_date} ${inv.due_date}`.toLowerCase();
          return hay.includes(q);
        })
      : list;

    return [...searched].sort((a, b) => {
      const dueA = Date.parse(a.due_date || "");
      const dueB = Date.parse(b.due_date || "");
      const amtA = Number(a.total_amount ?? 0);
      const amtB = Number(b.total_amount ?? 0);

      switch (sortBy) {
        case "due_asc":
          return dueA - dueB;
        case "amount_desc":
          return amtB - amtA;
        case "amount_asc":
          return amtA - amtB;
        case "due_desc":
        default:
          return dueB - dueA;
      }
    });
  }, [invoices.data, query, sortBy]);

  const isPaid = status === "paid";

  return (
    <div className="space-y-5">
      <AnimatedSection>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${isPaid ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300" : "bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300"}`}>
              <Receipt size={22} />
            </div>
            <div>
              <h1 className="font-display text-3xl font-bold">{isPaid ? "Paid Invoices" : "Unpaid Invoices"}</h1>
              <p className="text-muted-foreground text-sm">{filteredInvoices.length} invoices shown</p>
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
                placeholder="Search by company, invoice id, or date"
                className="pl-9"
              />
            </div>
            <div className="w-full md:w-56">
              <Select value={sortBy} onValueChange={(v) => setSortBy(v as SortMode)}>
                <SelectTrigger>
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="due_desc">Due Date: Newest</SelectItem>
                  <SelectItem value="due_asc">Due Date: Oldest</SelectItem>
                  <SelectItem value="amount_desc">Amount: High to Low</SelectItem>
                  <SelectItem value="amount_asc">Amount: Low to High</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {invoices.isLoading ? (
            <div className="space-y-2 py-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-11 w-full rounded-lg" />
              ))}
            </div>
          ) : filteredInvoices.length > 0 ? (
            <div className="overflow-x-auto rounded-xl border border-border/60">
              <table className="w-full text-sm">
                <thead className="bg-muted/45">
                  <tr className="text-left">
                    <th className="px-4 py-3 font-semibold text-muted-foreground">ID</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Company</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Period</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Due Date</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Total</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredInvoices.map((inv, idx) => (
                    <motion.tr
                      key={inv.id}
                      initial={{ opacity: 0, y: 6 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.18, delay: idx * 0.015 }}
                      className="border-t border-border/60 hover:bg-muted/40 transition-colors"
                    >
                      <td className="px-4 py-3">#{inv.id}</td>
                      <td className="px-4 py-3">{inv.company_name ?? `Company #${inv.company_id}`}</td>
                      <td className="px-4 py-3">{inv.start_date} - {inv.end_date}</td>
                      <td className="px-4 py-3">{inv.due_date}</td>
                      <td className="px-4 py-3 font-semibold">
                        {inv.total_amount ? `AED ${Number(inv.total_amount).toFixed(2)}` : "-"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-2">
                          <Button size="sm" variant="outline" onClick={() => handleDownloadPdf(inv.id)}>
                            <Download size={14} className="mr-1" /> PDF
                          </Button>
                          {!isPaid && (
                            <Button
                              size="sm"
                              onClick={() => markPaid.mutate(inv.id)}
                              disabled={markPaid.isPending}
                              className="bg-accent-gradient text-accent-foreground border-0"
                            >
                              <CheckCircle2 size={14} className="mr-1" /> Paid
                            </Button>
                          )}
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-16 text-center bg-muted/20">
              <CircleAlert size={42} className="mx-auto text-muted-foreground/60 mb-4" />
              <p className="font-semibold text-lg">No {status} invoices found.</p>
              <p className="text-sm text-muted-foreground mt-1">Try adjusting your search filters.</p>
            </div>
          )}
        </div>
      </AnimatedSection>
    </div>
  );
};

export default CompaniesPage;
