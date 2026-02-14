export type ContactRequestInput = {
  name: string;
  email: string;
  phone: string;
  subject: string;
  message: string;
  sourcePage?: string;
};

export type ContactRequestApi = {
  id: number;
  name: string;
  email: string;
  phone: string;
  subject: string;
  message: string;
  status: string;
  source_page: string;
  created_at: string;
  updated_at: string;
};

export type QuoteRequestInput = {
  name: string;
  email: string;
  mobile: string;
  freight: string;
  origin: string;
  destination: string;
  note?: string;
};

export type QuoteRequestApi = {
  id: number;
  name: string;
  email: string;
  mobile: string;
  freight: string;
  origin: string;
  destination: string;
  note: string;
  status: string;
  created_at: string;
  updated_at: string;
};
