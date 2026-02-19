import { apiClient } from "./apiClient";
import { sensitiveExportStepUpHeaders } from "./stepUp";
import type {
  EmployeeSalaryApi,
  EmployeeSalaryCreateInput,
  EmployeeSalaryImportResult,
  EmployeeSalaryUpdateInput,
} from "@/types";

export const listEmployeeSalaries = async (): Promise<EmployeeSalaryApi[]> => {
  const response = await apiClient.get<EmployeeSalaryApi[]>("/employee-salaries");
  return response.data;
};

export const createEmployeeSalary = async (
  payload: EmployeeSalaryCreateInput,
): Promise<EmployeeSalaryApi> => {
  const response = await apiClient.post<EmployeeSalaryApi>("/employee-salaries", {
    employee_name: payload.employeeName,
    work_permit_no: payload.workPermitNo,
    personal_no: payload.personalNo,
    bank_name_routing_no: payload.bankNameRoutingNo || null,
    bank_account_no: payload.bankAccountNo,
    days_absent: payload.daysAbsent ?? null,
    fixed_portion: payload.fixedPortion,
    variable_portion: payload.variablePortion,
    total_payment: payload.totalPayment || undefined,
    on_leave: payload.onLeave,
  });
  return response.data;
};

export const updateEmployeeSalary = async (
  employeeId: number,
  payload: EmployeeSalaryUpdateInput,
): Promise<EmployeeSalaryApi> => {
  const response = await apiClient.patch<EmployeeSalaryApi>(`/employee-salaries/${employeeId}`, {
    ...(payload.employeeName !== undefined ? { employee_name: payload.employeeName } : {}),
    ...(payload.workPermitNo !== undefined ? { work_permit_no: payload.workPermitNo } : {}),
    ...(payload.personalNo !== undefined ? { personal_no: payload.personalNo } : {}),
    ...(payload.bankNameRoutingNo !== undefined ? { bank_name_routing_no: payload.bankNameRoutingNo || null } : {}),
    ...(payload.bankAccountNo !== undefined ? { bank_account_no: payload.bankAccountNo } : {}),
    ...(payload.daysAbsent !== undefined ? { days_absent: payload.daysAbsent } : {}),
    ...(payload.fixedPortion !== undefined ? { fixed_portion: payload.fixedPortion } : {}),
    ...(payload.variablePortion !== undefined ? { variable_portion: payload.variablePortion } : {}),
    ...(payload.totalPayment !== undefined ? { total_payment: payload.totalPayment } : {}),
    ...(payload.onLeave !== undefined ? { on_leave: payload.onLeave } : {}),
  });
  return response.data;
};

export const deleteEmployeeSalary = async (employeeId: number): Promise<void> => {
  await apiClient.delete(`/employee-salaries/${employeeId}`);
};

export const exportEmployeeSalaries = async (month: number, year: number): Promise<Blob> => {
  const response = await apiClient.get("/employee-salaries/export", {
    params: { month, year },
    responseType: "blob",
    headers: sensitiveExportStepUpHeaders(),
  });
  return response.data as Blob;
};

export const importEmployeeSalaries = async (file: File): Promise<EmployeeSalaryImportResult> => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post<EmployeeSalaryImportResult>("/employee-salaries/import", formData);
  return response.data;
};
