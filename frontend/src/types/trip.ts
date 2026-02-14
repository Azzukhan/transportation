export interface TripApi {
  id: number;
  company_id: number;
  date: string;
  freight: string;
  origin: string;
  destination: string;
  amount: string;
  toll_gate: string;
  driver: string;
  vat: string;
  total_amount: string;
  paid: boolean;
  invoice_id: number | null;
  created_at?: string;
  company_name?: string;
}

export interface TripCreateInput {
  companyId: number;
  date: string;
  freight: string;
  origin: string;
  destination: string;
  amount: number;
  tollGate: number;
  driver: string;
}
