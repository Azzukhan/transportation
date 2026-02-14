export interface InvoiceApi {
  id: number;
  company_id: number;
  start_date: string;
  end_date: string;
  due_date: string;
  format_key: string;
  status: string;
  total_amount?: string;
  created_at?: string;
  company_name?: string;
}

export interface InvoiceCreateInput {
  companyId: number;
  startDate?: string;
  endDate?: string;
  dueDate?: string;
  formatKey: string;
  tripIds?: number[];
}
