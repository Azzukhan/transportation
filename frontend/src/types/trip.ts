export type TripApi = {
  id: number;
  company_id: number;
  date: string;
  freight: string;
  origin: string;
  destination: string;
  amount: string;
  toll_gate: string;
  vat: string;
  total_amount: string;
  driver: string;
  paid: boolean;
};

export type TripCreateInput = {
  companyId: number;
  date: string;
  freight: string;
  origin: string;
  destination: string;
  amount: number;
  tollGate: number;
  driver: string;
};
