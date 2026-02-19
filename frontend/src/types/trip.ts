export interface TripApi {
  id: number;
  company_id: number;
  date: string;
  freight: string;
  origin: string;
  destination: string;
  destination_company_name?: string | null;
  trip_category?: "domestic" | "international";
  amount: string;
  toll_gate: string;
  driver: string;
  driver_id?: number | null;
  external_driver_name?: string | null;
  external_driver_mobile?: string | null;
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
  destinationCompanyName?: string;
  tripCategory: "domestic" | "international";
  amount: number;
  tollGate: number;
  driver: string;
  driverId?: number;
  externalDriverName?: string;
  externalDriverMobile?: string;
}
