import { apiClient } from "./apiClient";
import type { InvoiceApi, InvoiceCreateInput } from "../types";

export const listInvoices = async (status?: string): Promise<InvoiceApi[]> => {
  const response = await apiClient.get<InvoiceApi[]>("/invoices", {
    params: status ? { status } : undefined,
  });
  return response.data;
};

export const createInvoice = async (payload: InvoiceCreateInput): Promise<InvoiceApi> => {
  const response = await apiClient.post<InvoiceApi>("/invoices", {
    company_id: payload.companyId,
    start_date: payload.startDate,
    end_date: payload.endDate,
    due_date: payload.dueDate,
    format_key: payload.formatKey,
    trip_ids: payload.tripIds ?? [],
  });
  return response.data;
};

export const markInvoicePaid = async (invoiceId: number): Promise<InvoiceApi> => {
  const response = await apiClient.patch<InvoiceApi>(`/invoices/${invoiceId}/mark-paid`, {});
  return response.data;
};

export const downloadInvoicePdf = async (invoiceId: number, templateKey?: string): Promise<Blob> => {
  const response = await apiClient.get<Blob>(`/invoices/${invoiceId}/pdf`, {
    params: templateKey ? { template: templateKey } : undefined,
    responseType: "blob",
  });
  return response.data;
};
