export interface EmployeeSalaryApi {
  id: number;
  employee_name: string;
  work_permit_no: string;
  personal_no: string;
  bank_name_routing_no?: string | null;
  bank_account_no: string;
  days_absent?: number | null;
  fixed_portion: string;
  variable_portion: string;
  total_payment: string;
  on_leave: boolean;
}

export interface EmployeeSalaryCreateInput {
  employeeName: string;
  workPermitNo: string;
  personalNo: string;
  bankNameRoutingNo?: string;
  bankAccountNo: string;
  daysAbsent?: number | null;
  fixedPortion: string;
  variablePortion: string;
  totalPayment?: string;
  onLeave: boolean;
}

export interface EmployeeSalaryUpdateInput extends Partial<EmployeeSalaryCreateInput> {}

export interface EmployeeSalaryImportSkipped {
  row_number: number;
  reason: string;
}

export interface EmployeeSalaryImportResult {
  created: number;
  updated: number;
  skipped: EmployeeSalaryImportSkipped[];
}
