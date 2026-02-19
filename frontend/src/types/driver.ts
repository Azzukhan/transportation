export interface DriverApi {
  id: number;
  name: string;
  mobile_number: string;
  passport_number?: string | null;
  emirates_id_number?: string | null;
  emirates_id_expiry_date?: string | null;
}

export interface DriverCreateInput {
  name: string;
  mobileNumber: string;
  passportNumber?: string;
  emiratesIdNumber?: string;
  emiratesIdExpiryDate?: string;
}
