import { useCallback, useEffect, useMemo, useState } from "react";

import { createCompany, listCompanies } from "../api/companies";
import type {
  Company,
  CompanyApi,
  CompanyCreateInput,
  CompanyDashboardSummary,
} from "../types";
import { toast } from "../utils/toast";

const parseMoney = (value: string): number => {
  const amount = Number(value);
  return Number.isNaN(amount) ? 0 : amount;
};

const mapCompany = (company: CompanyApi): Company => ({
  id: company.id,
  name: company.name,
  address: company.address,
  email: company.email,
  phone: company.phone,
  contactPerson: company.contact_person,
  poBox: company.po_box,
  paidAmount: parseMoney(company.paid_amount),
  unpaidAmount: parseMoney(company.unpaid_amount),
});

export const useCompanies = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCompanies = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await listCompanies();
      setCompanies(response.map(mapCompany));
    } catch {
      const message = "Failed to load companies.";
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchCompanies();
  }, [fetchCompanies]);

  const summary: CompanyDashboardSummary = useMemo(() => {
    return {
      totalCompanies: companies.length,
      totalPaidAmount: companies.reduce((sum, company) => sum + company.paidAmount, 0),
      totalUnpaidAmount: companies.reduce((sum, company) => sum + company.unpaidAmount, 0),
    };
  }, [companies]);

  const addCompany = useCallback(
    async (payload: CompanyCreateInput): Promise<boolean> => {
      try {
        const created = await createCompany(payload);
        setCompanies((current) => [mapCompany(created), ...current]);
        toast.success("Company created successfully.");
        return true;
      } catch {
        toast.error("Failed to create company.");
        return false;
      }
    },
    [],
  );

  return {
    companies,
    summary,
    isLoading,
    error,
    refetch: fetchCompanies,
    addCompany,
  };
};
