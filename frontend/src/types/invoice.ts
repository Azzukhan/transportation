export interface InvoiceApi {
  id: number;
  company_id: number;
  start_date: string;
  end_date: string;
  due_date: string;
  invoice_number?: string | null;
  format_key: string;
  prepared_by_mode?: "without_signature" | "with_signature";
  signatory_id?: number | null;
  signatory_name?: string | null;
  signatory_image_path?: string | null;
  signatory_image_mime?: string | null;
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
  invoiceNumber?: string;
  preparedByMode: "without_signature" | "with_signature";
  signatoryId?: number;
  formatKey: string;
  tripIds?: number[];
}

export interface SignatoryApi {
  id: number;
  name: string;
  signature_image_mime?: string | null;
  has_signature: boolean;
}
