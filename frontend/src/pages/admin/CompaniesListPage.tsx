import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listCompanies } from "@/api/companies";
import { AnimatedSection } from "@/components/AnimatedSection";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Building2, Plus, UsersRound } from "lucide-react";

const CompaniesListPage = () => {
  const companies = useQuery({ queryKey: ["companies"], queryFn: listCompanies });

  const sortedCompanies = useMemo(
    () => [...(companies.data ?? [])].sort((a, b) => a.id - b.id),
    [companies.data],
  );

  return (
    <div className="space-y-5">
      <AnimatedSection>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300 flex items-center justify-center">
                <UsersRound size={22} />
              </div>
              <div>
                <h1 className="font-display text-3xl font-bold">Companies</h1>
                <p className="text-muted-foreground text-sm">{sortedCompanies.length} companies registered</p>
              </div>
            </div>
            <Button asChild className="bg-accent-gradient text-accent-foreground border-0">
              <Link to="/add_company">
                <Plus size={15} className="mr-1" /> Add Company
              </Link>
            </Button>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.08}>
        <div className="bg-card rounded-2xl p-5 md:p-6 shadow-card border border-border/60">
          {companies.isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-11 w-full rounded-lg" />
              ))}
            </div>
          ) : sortedCompanies.length > 0 ? (
            <div className="overflow-x-auto rounded-xl border border-border/60">
              <table className="w-full text-sm">
                <thead className="bg-muted/45">
                  <tr className="text-left">
                    <th className="px-4 py-3 font-semibold text-muted-foreground">ID</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Company</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">TRN</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Phone</th>
                    <th className="px-4 py-3 font-semibold text-muted-foreground">Email</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedCompanies.map((company) => (
                    <tr key={company.id} className="border-t border-border/60 hover:bg-muted/40 transition-colors">
                      <td className="px-4 py-3">#{company.id}</td>
                      <td className="px-4 py-3 font-medium">{company.name}</td>
                      <td className="px-4 py-3">{company.trn}</td>
                      <td className="px-4 py-3">{company.phone}</td>
                      <td className="px-4 py-3">{company.email}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-16 text-center bg-muted/20">
              <Building2 size={42} className="mx-auto text-muted-foreground/60 mb-4" />
              <p className="font-semibold text-lg">No companies found.</p>
              <p className="text-sm text-muted-foreground mt-1">Add your first company to start trip and invoice flow.</p>
            </div>
          )}

        </div>
      </AnimatedSection>
    </div>
  );
};

export default CompaniesListPage;
