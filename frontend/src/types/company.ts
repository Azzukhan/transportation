export interface CompanyApi {
  id: number;
  name: string;
  address: string;
  email: string;
  phone: string;
  contact_person: string;
  po_box: string;
  created_at?: string;
  updated_at?: string;
}

export interface CompanyCreateInput {
  name: string;
  address: string;
  email: string;
  phone: string;
  contactPerson: string;
  poBox: string;
}
