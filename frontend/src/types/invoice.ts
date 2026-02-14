export type InvoiceApi = {
  id: number;
  company_id: number;
  start_date: string;
  end_date: string;
  due_date: string;
  format_key: string;
  total_amount: string;
  generated_at: string;
  paid_at: string | null;
  status: "paid" | "unpaid" | "overdue";
};

export type InvoiceCreateInput = {
  companyId: number;
  startDate: string;
  endDate: string;
  dueDate?: string;
  formatKey: string;
};
