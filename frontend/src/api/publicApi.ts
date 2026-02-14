import { apiClient } from "./apiClient";
import type {
  ContactRequestApi,
  ContactRequestInput,
  QuoteRequestApi,
  QuoteRequestInput,
} from "../types";

export const submitContactRequest = async (payload: ContactRequestInput): Promise<ContactRequestApi> => {
  const response = await apiClient.post<ContactRequestApi>("/public/contact-requests", {
    name: payload.name,
    email: payload.email,
    phone: payload.phone,
    subject: payload.subject,
    message: payload.message,
    source_page: payload.sourcePage ?? "contact",
  });
  return response.data;
};

export const submitQuoteRequest = async (payload: QuoteRequestInput): Promise<QuoteRequestApi> => {
  const response = await apiClient.post<QuoteRequestApi>("/public/quote-requests", {
    name: payload.name,
    email: payload.email,
    mobile: payload.mobile,
    freight: payload.freight,
    origin: payload.origin,
    destination: payload.destination,
    note: payload.note ?? "",
  });
  return response.data;
};

export const listContactRequests = async (): Promise<ContactRequestApi[]> => {
  const response = await apiClient.get<ContactRequestApi[]>("/public/contact-requests");
  return response.data;
};

export const listQuoteRequests = async (): Promise<QuoteRequestApi[]> => {
  const response = await apiClient.get<QuoteRequestApi[]>("/public/quote-requests");
  return response.data;
};

export const updateContactRequestStatus = async (requestId: number, status: string): Promise<ContactRequestApi> => {
  const response = await apiClient.patch<ContactRequestApi>(`/public/contact-requests/${requestId}`, { status });
  return response.data;
};

export const updateQuoteRequestStatus = async (requestId: number, status: string): Promise<QuoteRequestApi> => {
  const response = await apiClient.patch<QuoteRequestApi>(`/public/quote-requests/${requestId}`, { status });
  return response.data;
};
