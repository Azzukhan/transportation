import { useMemo } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { listCompanies } from "@/api/companies";
import { listTrips } from "@/api/trips";
import { listInvoices } from "@/api/invoices";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Skeleton } from "@/components/ui/skeleton";
import { Building2, Truck, FileText, HandCoins, ArrowUpRight, PackageOpen } from "lucide-react";

const DashboardPage = () => {
  const companies = useQuery({ queryKey: ["companies"], queryFn: () => listCompanies() });
  const trips = useQuery({ queryKey: ["trips"], queryFn: () => listTrips() });
  const invoicesPaid = useQuery({ queryKey: ["invoices", "paid"], queryFn: () => listInvoices("paid") });
  const invoicesUnpaid = useQuery({ queryKey: ["invoices", "unpaid"], queryFn: () => listInvoices("unpaid") });

  const loadingMetrics = companies.isLoading || trips.isLoading || invoicesPaid.isLoading || invoicesUnpaid.isLoading;

  const totalRevenue = useMemo(() => {
    if (!invoicesPaid.data) return 0;
    return invoicesPaid.data.reduce((sum, inv) => sum + Number(inv.total_amount ?? 0), 0);
  }, [invoicesPaid.data]);

  const stats = [
    {
      icon: Building2,
      label: "Total Companies",
      value: companies.data?.length ?? 0,
      note: "Registered clients",
      cardClass: "bg-sky-50 border-sky-100 dark:bg-sky-950/25 dark:border-sky-900/40",
      iconClass: "bg-sky-200/70 text-sky-700 dark:bg-sky-900/50 dark:text-sky-300",
    },
    {
      icon: Truck,
      label: "Total Trips",
      value: trips.data?.length ?? 0,
      note: "Transportation entries",
      cardClass: "bg-orange-50 border-orange-100 dark:bg-orange-950/20 dark:border-orange-900/40",
      iconClass: "bg-orange-200/70 text-orange-700 dark:bg-orange-900/45 dark:text-orange-300",
    },
    {
      icon: FileText,
      label: "Paid Invoices",
      value: invoicesPaid.data?.length ?? 0,
      note: `Revenue AED ${totalRevenue.toFixed(2)}`,
      cardClass: "bg-emerald-50 border-emerald-100 dark:bg-emerald-950/20 dark:border-emerald-900/40",
      iconClass: "bg-emerald-200/70 text-emerald-700 dark:bg-emerald-900/45 dark:text-emerald-300",
    },
    {
      icon: HandCoins,
      label: "Unpaid Invoices",
      value: invoicesUnpaid.data?.length ?? 0,
      note: "Pending collections",
      cardClass: "bg-rose-50 border-rose-100 dark:bg-rose-950/20 dark:border-rose-900/40",
      iconClass: "bg-rose-200/70 text-rose-700 dark:bg-rose-900/45 dark:text-rose-300",
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <AnimatedSection>
        <section className="rounded-2xl p-6 md:p-8 text-primary-foreground bg-[linear-gradient(120deg,hsl(var(--primary))_0%,hsl(219_52%_35%)_100%)] shadow-elevated border border-primary/30">
          <p className="text-sm font-semibold text-accent mb-2 flex items-center gap-1.5">
            <ArrowUpRight size={14} /> Dashboard Overview
          </p>
          <h1 className="font-display text-3xl md:text-4xl font-bold mb-2">Welcome Back</h1>
          <p className="text-primary-foreground/75 text-base md:text-lg max-w-2xl">
            Here is a live summary of company records, trip activity, and invoice status across your transport operations.
          </p>
        </section>
      </AnimatedSection>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {loadingMetrics
          ? Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="rounded-2xl border p-5 shadow-card bg-card">
                <div className="flex items-start justify-between mb-4">
                  <Skeleton className="w-11 h-11 rounded-xl" />
                  <Skeleton className="w-10 h-4" />
                </div>
                <Skeleton className="w-20 h-10 mb-2" />
                <Skeleton className="w-32 h-4 mb-2" />
                <Skeleton className="w-24 h-3" />
              </div>
            ))
          : stats.map((stat, i) => (
              <AnimatedSection key={stat.label} delay={i * 0.08}>
                <div className={`rounded-2xl border p-5 shadow-card ${stat.cardClass}`}>
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${stat.iconClass}`}>
                      <stat.icon size={20} />
                    </div>
                    <span className="text-xs font-semibold text-foreground/60">Live</span>
                  </div>
                  <div className="font-display text-4xl font-bold leading-none mb-2">{stat.value}</div>
                  <p className="text-sm font-semibold">{stat.label}</p>
                  <p className="text-xs text-muted-foreground mt-1">{stat.note}</p>
                </div>
              </AnimatedSection>
            ))}
      </div>

      <AnimatedSection delay={0.25}>
        <div className="bg-card rounded-2xl p-6 md:p-7 shadow-card border border-border/60">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-display font-bold text-2xl">Recent Trips</h3>
              <p className="text-sm text-muted-foreground">Latest transportation activities</p>
            </div>
            <span className="text-xs px-3 py-1 rounded-full border border-border bg-muted/60">
              {trips.data?.length ?? 0} total
            </span>
          </div>

          {trips.isLoading ? (
            <div className="space-y-2 py-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-11 w-full rounded-lg" />
              ))}
            </div>
          ) : trips.data && trips.data.length > 0 ? (
            <div className="overflow-x-auto rounded-xl border border-border/60">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr className="text-left">
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Date</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Freight</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Origin</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Destination</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Driver</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {trips.data.slice(0, 10).map((trip, idx) => (
                    <motion.tr
                      key={trip.id}
                      initial={{ opacity: 0, y: 6 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.18, delay: idx * 0.02 }}
                      className="border-t border-border/60 hover:bg-muted/40 transition-colors"
                    >
                      <td className="px-4 py-3">{trip.date}</td>
                      <td className="px-4 py-3">{trip.freight}</td>
                      <td className="px-4 py-3">{trip.origin}</td>
                      <td className="px-4 py-3">{trip.destination}</td>
                      <td className="px-4 py-3">{trip.driver}</td>
                      <td className="px-4 py-3 text-right font-semibold">AED {Number(trip.amount).toFixed(2)}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-16 text-center bg-muted/20">
              <PackageOpen size={44} className="mx-auto text-muted-foreground/60 mb-4" />
              <p className="font-semibold text-lg">No trips found yet.</p>
              <p className="text-sm text-muted-foreground mt-1">Add your first trip to start tracking operations.</p>
            </div>
          )}
        </div>
      </AnimatedSection>
    </div>
  );
};

export default DashboardPage;
