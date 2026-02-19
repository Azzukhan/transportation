export interface ContactRequestApi {
  id: number;
  name: string;
  email: string;
  phone: string;
  subject: string;
  message: string;
  source_page: string;
  status: string;
  created_at?: string;
}

export interface ContactRequestInput {
  name: string;
  email: string;
  phone: string;
  subject: string;
  message: string;
  sourcePage?: string;
}

export interface QuoteRequestApi {
  id: number;
  name: string;
  email: string;
  mobile: string;
  freight: string;
  origin: string;
  destination: string;
  note: string;
  status: string;
  created_at?: string;
}

export interface QuoteRequestUpdateInput {
  name?: string;
  email?: string;
  mobile?: string;
  freight?: string;
  origin?: string;
  destination?: string;
  note?: string;
  status?: string;
}

export interface QuoteRequestInput {
  name: string;
  email: string;
  mobile: string;
  freight: string;
  origin: string;
  destination: string;
  note?: string;
}
