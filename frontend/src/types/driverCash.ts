export interface DriverCashHandoverApi {
  id: number;
  driver_id: number;
  driver_name: string;
  handover_date: string;
  amount: string;
  notes?: string | null;
}

export interface DriverCashHandoverCreateInput {
  driverId: number;
  handoverDate: string;
  amount: number;
  notes?: string;
}

export interface DriverCashSummaryApi {
  driver_id: number;
  driver_name: string;
  trip_count: number;
  earned_amount_total: string;
  handover_amount_total: string;
  balance_amount: string;
}
