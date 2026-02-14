export type CompanyApi = {
  id: number;
  name: string;
  address: string;
  email: string;
  phone: string;
  contact_person: string;
  po_box: string;
  paid_amount: string;
  unpaid_amount: string;
};

export type Company = {
  id: number;
  name: string;
  address: string;
  email: string;
  phone: string;
  contactPerson: string;
  poBox: string;
  paidAmount: number;
  unpaidAmount: number;
};

export type CompanyCreateInput = {
  name: string;
  address: string;
  email: string;
  phone: string;
  contactPerson: string;
  poBox: string;
};

export type CompanyDashboardSummary = {
  totalCompanies: number;
  totalPaidAmount: number;
  totalUnpaidAmount: number;
};
