import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";

import { PublicLayout } from "@/components/Layout/PublicLayout";
import { AdminLayout } from "@/components/Layout/AdminLayout";

import HomePage from "@/pages/HomePage";
import AboutPage from "@/pages/AboutPage";
import ContactPage from "@/pages/ContactPage";
import { ServiceListPage, ServiceDetailPage } from "@/pages/ServicePages";
import QuotePage from "@/pages/QuotePage";
import LiveOperationsPage from "@/pages/LiveOperationsPage";
import LoginPage from "@/pages/LoginPage";

import DashboardPage from "@/pages/admin/DashboardPage";
import AddCompanyPage from "@/pages/admin/AddCompanyPage";
import AddTripPage from "@/pages/admin/AddTripPage";
import CompaniesListPage from "@/pages/admin/CompaniesListPage";
import TripsListPage from "@/pages/admin/TripsListPage";
import DriversPage from "@/pages/admin/DriversPage";
import DriverCashPage from "@/pages/admin/DriverCashPage";
import EmployeeSalariesPage from "@/pages/admin/EmployeeSalariesPage";
import CreateInvoicePage from "@/pages/admin/CreateInvoicePage";
import CreateQuotePage from "@/pages/admin/CreateQuotePage";
import CompaniesPage from "@/pages/admin/CompaniesPage";
import ContactRequestsPage from "@/pages/admin/ContactRequestsPage";
import QuoteRequestsPage from "@/pages/admin/QuoteRequestsPage";
import SignatoriesPage from "@/pages/admin/SignatoriesPage";
import NotFound from "@/pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route element={<PublicLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="/service" element={<ServiceListPage />} />
              <Route path="/service/:slug" element={<ServiceDetailPage />} />
              <Route path="/live-operations" element={<LiveOperationsPage />} />
              <Route path="/quote" element={<QuotePage />} />
            </Route>

            {/* Auth */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected admin routes */}
            <Route element={<ProtectedRoute><AdminLayout /></ProtectedRoute>}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/companies" element={<CompaniesListPage />} />
              <Route path="/add_company" element={<AddCompanyPage />} />
              <Route path="/trips" element={<TripsListPage />} />
              <Route path="/drivers" element={<DriversPage />} />
              <Route path="/driver-cash" element={<DriverCashPage />} />
              <Route path="/employee-salaries" element={<EmployeeSalariesPage />} />
              <Route path="/add_trip" element={<AddTripPage />} />
              <Route path="/create-invoice" element={<CreateInvoicePage />} />
              <Route path="/create-quote" element={<CreateQuotePage />} />
              <Route path="/paid-companies" element={<CompaniesPage status="paid" />} />
              <Route path="/unpaid-companies" element={<CompaniesPage status="unpaid" />} />
              <Route path="/contact-requests" element={<ContactRequestsPage />} />
              <Route path="/quote-requests" element={<QuoteRequestsPage />} />
              <Route path="/signatories" element={<SignatoriesPage />} />
            </Route>

            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
