import { apiClient } from "./apiClient";
import type {
  DriverCashHandoverApi,
  DriverCashHandoverCreateInput,
  DriverCashSummaryApi,
} from "@/types";

export const listDriverCashHandovers = async (filters?: {
  driverId?: number;
  startDate?: string;
  endDate?: string;
}): Promise<DriverCashHandoverApi[]> => {
  const response = await apiClient.get<DriverCashHandoverApi[]>("/driver-cash-handovers", {
    params: {
      ...(filters?.driverId ? { driver_id: filters.driverId } : {}),
      ...(filters?.startDate ? { start_date: filters.startDate } : {}),
      ...(filters?.endDate ? { end_date: filters.endDate } : {}),
    },
  });
  return response.data;
};

export const createDriverCashHandover = async (
  payload: DriverCashHandoverCreateInput,
): Promise<DriverCashHandoverApi> => {
  const response = await apiClient.post<DriverCashHandoverApi>("/driver-cash-handovers", {
    driver_id: payload.driverId,
    handover_date: payload.handoverDate,
    amount: payload.amount.toFixed(2),
    notes: payload.notes?.trim() || null,
  });
  return response.data;
};

export const getDriverCashSummary = async (filters?: {
  driverId?: number;
  startDate?: string;
  endDate?: string;
}): Promise<DriverCashSummaryApi[]> => {
  const response = await apiClient.get<DriverCashSummaryApi[]>("/driver-cash-handovers/summary", {
    params: {
      ...(filters?.driverId ? { driver_id: filters.driverId } : {}),
      ...(filters?.startDate ? { start_date: filters.startDate } : {}),
      ...(filters?.endDate ? { end_date: filters.endDate } : {}),
    },
  });
  return response.data;
};
