import { apiClient } from "./apiClient";
import type { TripApi, TripCreateInput } from "../types";

export const listTrips = async (companyId?: number): Promise<TripApi[]> => {
  const response = await apiClient.get<TripApi[]>("/trips", {
    params: companyId ? { company_id: companyId } : undefined,
  });
  return response.data;
};

export const createTrip = async (payload: TripCreateInput): Promise<TripApi> => {
  const response = await apiClient.post<TripApi>("/trips", {
    company_id: payload.companyId,
    date: payload.date,
    freight: payload.freight,
    origin: payload.origin,
    destination: payload.destination,
    amount: payload.amount.toFixed(2),
    toll_gate: payload.tollGate.toFixed(2),
    driver: payload.driver,
  });
  return response.data;
};
