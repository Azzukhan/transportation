import { Button, Card, Form, Input, Typography } from "antd";
import { ConfigProvider } from "antd";
import { BrowserRouter, Navigate, Outlet, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import { useAppDispatch } from "./app/hooks";
import { loginUser } from "./api/authentication";
import { AppLayout } from "./components/Layout/AppLayout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LogoLockup } from "./components/Brand/LogoLockup";
import { PublicShell } from "./components/Public/PublicShell";
import { onLoginSuccess } from "./features/auth/authSlice";
import {
  AboutRoute,
  AddCompanyRoute,
  AddTripRoute,
  ContactRoute,
  ContactRequestsRoute,
  DashboardRoute,
  FeatureRoute,
  HomeRoute,
  LiveOperationsRoute,
  PaidCompaniesRoute,
  QuoteRequestsRoute,
  QuoteRoute,
  ServiceDetailRoute,
  ServiceRoute,
  UnpaidCompaniesRoute,
} from "./routes";
import { toast } from "./utils";

const { Title, Paragraph } = Typography;
type LoginFormValues = { username: string; password: string };

const NotFoundPage = () => (
  <Card>
    <Title level={3}>Not Found</Title>
    <Paragraph>The page you requested does not exist.</Paragraph>
  </Card>
);

const LoginPage = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const redirectParam = new URLSearchParams(location.search).get("redirect");
  const redirectTo = redirectParam ? decodeURIComponent(redirectParam) : "/dashboard";

  const [form] = Form.useForm<LoginFormValues>();

  const handleLogin = async (values: LoginFormValues): Promise<void> => {
    try {
      const result = await loginUser(values);
      dispatch(onLoginSuccess(result));
      navigate(redirectTo, { replace: true });
    } catch {
      toast.error("Login failed. Please check your credentials.");
    }
  };

  return (
    <main className="login-screen">
      <Card className="login-card">
        <div className="login-brand">
          <LogoLockup size="lg" subtitle="Admin Workspace" />
        </div>
        <Title level={3}>Login</Title>
        <Paragraph>Sign in to access admin operations, invoicing, and request management.</Paragraph>
        <Form<LoginFormValues>
          layout="vertical"
          form={form}
          onFinish={(values) => void handleLogin(values)}
          style={{ marginTop: 12 }}
        >
          <Form.Item label="Username" name="username" rules={[{ required: true }]}>
            <Input autoComplete="username" />
          </Form.Item>
          <Form.Item label="Password" name="password" rules={[{ required: true }]}>
            <Input.Password autoComplete="current-password" />
          </Form.Item>
          <Button type="primary" htmlType="submit">
            Login
          </Button>
        </Form>
      </Card>
    </main>
  );
};

const ProtectedAppShell = () => (
  <ProtectedRoute>
    <AppLayout>
      <Outlet />
    </AppLayout>
  </ProtectedRoute>
);

export const App = () => {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#1f5da7",
          borderRadius: 10,
          colorText: "#10253b",
          colorTextSecondary: "#4f6278",
          colorBgContainer: "#ffffff",
        },
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route element={<PublicShell />}>
            <Route path="/" element={<HomeRoute />} />
            <Route path="/about" element={<AboutRoute />} />
            <Route path="/contact" element={<ContactRoute />} />
            <Route path="/service" element={<ServiceRoute />} />
            <Route path="/service/:slug" element={<ServiceDetailRoute />} />
            <Route path="/live-operations" element={<LiveOperationsRoute />} />
            <Route path="/feature" element={<FeatureRoute />} />
            <Route path="/quote" element={<QuoteRoute />} />
          </Route>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<ProtectedAppShell />}>
            <Route path="/dashboard" element={<DashboardRoute />} />
            <Route path="/add_company" element={<AddCompanyRoute />} />
            <Route path="/add_trip" element={<AddTripRoute />} />
            <Route path="/paid-companies" element={<PaidCompaniesRoute />} />
            <Route path="/unpaid-companies" element={<UnpaidCompaniesRoute />} />
            <Route path="/contact-requests" element={<ContactRequestsRoute />} />
            <Route path="/quote-requests" element={<QuoteRequestsRoute />} />
          </Route>

          <Route path="/404" element={<NotFoundPage />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
};
