import { apiClient } from "./apiClient";
import { sensitiveExportStepUpHeaders } from "./stepUp";
import type { TripApi, TripCreateInput } from "../types";

export const listTrips = async (filters?: {
  companyId?: number;
  paid?: boolean;
  driverId?: number;
  startDate?: string;
  endDate?: string;
}): Promise<TripApi[]> => {
  const response = await apiClient.get<TripApi[]>("/trips", {
    params: {
      ...(filters?.companyId ? { company_id: filters.companyId } : {}),
      ...(filters?.paid !== undefined ? { paid: filters.paid } : {}),
      ...(filters?.driverId ? { driver_id: filters.driverId } : {}),
      ...(filters?.startDate ? { start_date: filters.startDate } : {}),
      ...(filters?.endDate ? { end_date: filters.endDate } : {}),
    },
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
    destination_company_name: payload.destinationCompanyName || null,
    trip_category: payload.tripCategory,
    amount: payload.amount.toFixed(2),
    toll_gate: payload.tollGate.toFixed(2),
    driver: payload.driver,
    driver_id: payload.driverId,
    external_driver_name: payload.externalDriverName || null,
    external_driver_mobile: payload.externalDriverMobile || null,
  });
  return response.data;
};

export const getDriverReport = async (filters?: {
  driverId?: number;
  startDate?: string;
  endDate?: string;
}): Promise<Array<{ driver_name: string; trip_count: number; amount_excl_vat_total: string }>> => {
  const response = await apiClient.get<Array<{ driver_name: string; trip_count: number; amount_excl_vat_total: string }>>(
    "/trips/driver-report",
    {
      params: {
        ...(filters?.driverId ? { driver_id: filters.driverId } : {}),
        ...(filters?.startDate ? { start_date: filters.startDate } : {}),
        ...(filters?.endDate ? { end_date: filters.endDate } : {}),
      },
    },
  );
  return response.data;
};

export const downloadDriverReportCsv = async (filters?: {
  driverId?: number;
  startDate?: string;
  endDate?: string;
}): Promise<Blob> => {
  const response = await apiClient.get<Blob>("/trips/driver-report/export", {
    responseType: "blob",
    headers: sensitiveExportStepUpHeaders(),
    params: {
      ...(filters?.driverId ? { driver_id: filters.driverId } : {}),
      ...(filters?.startDate ? { start_date: filters.startDate } : {}),
      ...(filters?.endDate ? { end_date: filters.endDate } : {}),
    },
  });
  return response.data;
};
