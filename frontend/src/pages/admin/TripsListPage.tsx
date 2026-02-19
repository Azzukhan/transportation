import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { downloadDriverReportCsv, getDriverReport, listTrips } from "@/api/trips";
import { listCompanies } from "@/api/companies";
import { listDrivers } from "@/api/drivers";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Download, Plus, Route, Truck } from "lucide-react";
import { toast } from "sonner";

const TripsListPage = () => {
  const [companyFilter, setCompanyFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<"all" | "paid" | "unpaid">("all");
  const [driverFilter, setDriverFilter] = useState<string>("all");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const trips = useQuery({
    queryKey: ["trips", companyFilter, statusFilter, driverFilter, startDate, endDate],
    queryFn: () =>
      listTrips({
        companyId: companyFilter === "all" ? undefined : Number(companyFilter),
        paid: statusFilter === "all" ? undefined : statusFilter === "paid",
        driverId: driverFilter === "all" ? undefined : Number(driverFilter),
        startDate: startDate || undefined,
        endDate: endDate || undefined,
      }),
  });
  const companies = useQuery({ queryKey: ["companies"], queryFn: listCompanies });
  const drivers = useQuery({ queryKey: ["drivers"], queryFn: listDrivers });
  const driverReport = useQuery({
    queryKey: ["driver-report", driverFilter, startDate, endDate],
    queryFn: () =>
      getDriverReport({
        driverId: driverFilter === "all" ? undefined : Number(driverFilter),
        startDate: startDate || undefined,
        endDate: endDate || undefined,
      }),
  });

  const companyNamesById = useMemo(
    () => new Map((companies.data ?? []).map((company) => [company.id, company.name])),
    [companies.data],
  );

  const sortedTrips = useMemo(
    () => [...(trips.data ?? [])].sort((a, b) => Date.parse(b.date) - Date.parse(a.date)),
    [trips.data],
  );

  const companyOptions = useMemo(
    () => [...(companies.data ?? [])].sort((a, b) => a.id - b.id),
    [companies.data],
  );
  const driverOptions = useMemo(
    () => [...(drivers.data ?? [])].sort((a, b) => a.name.localeCompare(b.name)),
    [drivers.data],
  );

  const filteredTrips = useMemo(() => {
    return sortedTrips;
  }, [sortedTrips]);

  return (
    <div className="space-y-5">
      <AnimatedSection>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-orange-100 text-orange-700 dark:bg-orange-950/40 dark:text-orange-300 flex items-center justify-center">
                <Route size={22} />
              </div>
              <div>
                <h1 className="font-display text-3xl font-bold">Trips</h1>
                <p className="text-muted-foreground text-sm">{filteredTrips.length} trips shown</p>
              </div>
            </div>
            <Button asChild className="bg-accent-gradient text-accent-foreground border-0">
              <Link to="/add_trip">
                <Plus size={15} className="mr-1" /> Add Trip
              </Link>
            </Button>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.08}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex flex-col md:flex-row gap-3 mb-4">
            <div className="w-full md:w-80">
              <Select value={companyFilter} onValueChange={setCompanyFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Company" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Companies</SelectItem>
                  {companyOptions.map((company) => (
                    <SelectItem key={company.id} value={String(company.id)}>
                      #{company.id} - {company.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="w-full md:w-56">
              <Select value={statusFilter} onValueChange={(value: "all" | "paid" | "unpaid") => setStatusFilter(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Billing Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Billing Status</SelectItem>
                  <SelectItem value="paid">Invoiced</SelectItem>
                  <SelectItem value="unpaid">Not Invoiced</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="w-full md:w-72">
              <Select value={driverFilter} onValueChange={setDriverFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Driver" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Drivers</SelectItem>
                  {driverOptions.map((driver) => (
                    <SelectItem key={driver.id} value={String(driver.id)}>
                      {driver.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="w-full md:w-48">
              <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            </div>
            <div className="w-full md:w-48">
              <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>
            <Button
              type="button"
              variant="outline"
              onClick={async () => {
                try {
                  const blob = await downloadDriverReportCsv({
                    driverId: driverFilter === "all" ? undefined : Number(driverFilter),
                    startDate: startDate || undefined,
                    endDate: endDate || undefined,
                  });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = "driver_report.csv";
                  a.click();
                  URL.revokeObjectURL(url);
                } catch {
                  toast.error("Failed to download report.");
                }
              }}
            >
              <Download size={14} className="mr-1.5" /> Export Excel
            </Button>
          </div>

          <div className="rounded-xl border border-border/60 p-3 mb-4 bg-muted/20">
            <p className="text-sm font-semibold mb-2">Driver Trip Summary (Amount excl. VAT)</p>
            {driverReport.isLoading ? (
              <p className="text-xs text-muted-foreground">Loading summary...</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {(driverReport.data ?? []).map((row) => (
                  <span key={row.driver_name} className="text-xs px-2.5 py-1 rounded-full border border-border bg-background">
                    {row.driver_name}: {row.trip_count} trips, AED {Number(row.amount_excl_vat_total).toFixed(2)}
                  </span>
                ))}
                {(driverReport.data ?? []).length === 0 && (
                  <span className="text-xs text-muted-foreground">No data in selected range.</span>
                )}
              </div>
            )}
          </div>

          {trips.isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-11 w-full rounded-lg" />
              ))}
            </div>
          ) : filteredTrips.length > 0 ? (
            <div className="overflow-x-auto rounded-xl border border-border/60">
              <table className="w-full text-sm">
                <thead className="bg-muted/45">
                  <tr className="text-left">
                    <th className="px-4 py-3 font-semibold text-muted-foreground">ID</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Company</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Date</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Category</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Route</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Destination Company</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Driver</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Amount</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Billing Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTrips.map((trip) => (
                    <tr key={trip.id} className="border-t border-border/60 hover:bg-muted/40 transition-colors">
                      <td className="px-4 py-3">#{trip.id}</td>
                      <td className="px-4 py-3">{trip.company_name ?? companyNamesById.get(trip.company_id) ?? `Company #${trip.company_id}`}</td>
                      <td className="px-4 py-3">{trip.date}</td>
                      <td className="px-4 py-3 capitalize">{trip.trip_category ?? "domestic"}</td>
                      <td className="px-4 py-3">{trip.origin} - {trip.destination}</td>
                      <td className="px-4 py-3">{trip.destination_company_name || "-"}</td>
                      <td className="px-4 py-3">{trip.driver}</td>
                      <td className="px-4 py-3 font-medium">AED {Number(trip.total_amount ?? 0).toFixed(2)}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${trip.paid ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>
                          {trip.paid ? "Invoiced" : "Not Invoiced"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-16 text-center bg-muted/20">
              <Truck size={42} className="mx-auto text-muted-foreground/60 mb-4" />
              <p className="font-semibold text-lg">No trips found.</p>
              <p className="text-sm text-muted-foreground mt-1">Add your first trip to generate invoices.</p>
            </div>
          )}

        </div>
      </AnimatedSection>
    </div>
  );
};

export default TripsListPage;
