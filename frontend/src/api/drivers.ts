import { apiClient } from "./apiClient";
import type { DriverApi, DriverCreateInput } from "../types";

export const listDrivers = async (): Promise<DriverApi[]> => {
  const response = await apiClient.get<DriverApi[]>("/drivers");
  return response.data;
};

export const createDriver = async (payload: DriverCreateInput): Promise<DriverApi> => {
  const response = await apiClient.post<DriverApi>("/drivers", {
    name: payload.name,
    mobile_number: payload.mobileNumber,
    passport_number: payload.passportNumber || null,
    emirates_id_number: payload.emiratesIdNumber || null,
    emirates_id_expiry_date: payload.emiratesIdExpiryDate || null,
  });
  return response.data;
};
