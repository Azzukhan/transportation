import { apiClient } from "./apiClient";
import { sensitiveExportStepUpHeaders } from "./stepUp";
import type { InvoiceApi, InvoiceCreateInput, SignatoryApi } from "../types";

export const listInvoices = async (status?: string, companyId?: number): Promise<InvoiceApi[]> => {
  const response = await apiClient.get<InvoiceApi[]>("/invoices", {
    params: {
      ...(status ? { status } : {}),
      ...(companyId ? { company_id: companyId } : {}),
    },
  });
  return response.data;
};

export const createInvoice = async (payload: InvoiceCreateInput): Promise<InvoiceApi> => {
  const response = await apiClient.post<InvoiceApi>("/invoices", {
    company_id: payload.companyId,
    start_date: payload.startDate,
    end_date: payload.endDate,
    due_date: payload.dueDate,
    invoice_number: payload.invoiceNumber,
    prepared_by_mode: payload.preparedByMode,
    signatory_id: payload.signatoryId,
    format_key: payload.formatKey,
    trip_ids: payload.tripIds ?? [],
  });
  return response.data;
};

export const listSignatories = async (): Promise<SignatoryApi[]> => {
  const response = await apiClient.get<SignatoryApi[]>("/invoices/signatories");
  return response.data;
};

export const createSignatory = async (payload: {
  name: string;
  file: File;
}): Promise<SignatoryApi> => {
  const form = new FormData();
  form.append("name", payload.name);
  form.append("file", payload.file);
  const response = await apiClient.post<SignatoryApi>("/invoices/signatories", form, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const updateSignatory = async (
  signatoryId: number,
  payload: {
    name?: string;
    file?: File;
  },
): Promise<SignatoryApi> => {
  const form = new FormData();
  if (payload.name !== undefined) {
    form.append("name", payload.name);
  }
  if (payload.file !== undefined) {
    form.append("file", payload.file);
  }
  const response = await apiClient.patch<SignatoryApi>(`/invoices/signatories/${signatoryId}`, form, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const deleteSignatory = async (signatoryId: number): Promise<void> => {
  await apiClient.delete(`/invoices/signatories/${signatoryId}`);
};

export const downloadSignatorySignature = async (
  signatoryId: number,
): Promise<{ blob: Blob; mimeType: string }> => {
  const response = await apiClient.get<Blob>(`/invoices/signatories/${signatoryId}/signature`, {
    responseType: "blob",
  });
  return {
    blob: response.data,
    mimeType: (response.headers["content-type"] as string | undefined) || "application/octet-stream",
  };
};

export const markInvoicePaid = async (invoiceId: number): Promise<InvoiceApi> => {
  const response = await apiClient.patch<InvoiceApi>(`/invoices/${invoiceId}/mark-paid`, {});
  return response.data;
};

export const downloadInvoicePdf = async (
  invoiceId: number,
  templateKey?: string,
): Promise<{ blob: Blob; filename: string }> => {
  const response = await apiClient.get<Blob>(`/invoices/${invoiceId}/pdf`, {
    params: templateKey ? { template: templateKey } : undefined,
    responseType: "blob",
    headers: sensitiveExportStepUpHeaders(),
  });
  const disposition = response.headers["content-disposition"] as string | undefined;
  const fileNameMatch = disposition?.match(/filename="([^"]+)"/i);
  return {
    blob: response.data,
    filename: fileNameMatch?.[1] ?? `invoice-${invoiceId}.pdf`,
  };
};
