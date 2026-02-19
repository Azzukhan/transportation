import { apiClient } from "./apiClient";
import type { CompanyApi, CompanyCreateInput } from "../types";

const mapCompanyCreatePayload = (input: CompanyCreateInput) => ({
  name: input.name,
  address: input.address,
  email: input.email,
  phone: input.phone,
  trn: input.trn,
  contact_person: input.contactPerson,
  po_box: input.poBox,
});

export const listCompanies = async (): Promise<CompanyApi[]> => {
  const response = await apiClient.get<CompanyApi[]>("/companies");
  return response.data;
};

export const createCompany = async (payload: CompanyCreateInput): Promise<CompanyApi> => {
  const response = await apiClient.post<CompanyApi>("/companies", mapCompanyCreatePayload(payload));
  return response.data;
};

export const getCompany = async (companyId: number): Promise<CompanyApi> => {
  const response = await apiClient.get<CompanyApi>(`/companies/${companyId}`);
  return response.data;
};
