import { Menu, Typography } from "antd";
import {
  AppstoreOutlined,
  BankOutlined,
  DollarCircleOutlined,
  FileDoneOutlined,
  FormOutlined,
  HomeOutlined,
  TruckOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Link, useLocation } from "react-router-dom";

import { useAppSelector } from "../../app/hooks";
import { selectUser } from "../../features/auth/authSlice";
import { LogoLockup } from "../Brand/LogoLockup";

const { Title, Text } = Typography;

const items = [
  { key: "/dashboard", icon: <HomeOutlined />, label: <Link to="/dashboard">Dashboard</Link> },
  { key: "/add_company", icon: <BankOutlined />, label: <Link to="/add_company">Add Company</Link> },
  { key: "/add_trip", icon: <TruckOutlined />, label: <Link to="/add_trip">Add Trip</Link> },
  {
    key: "/paid-companies",
    icon: <FileDoneOutlined />,
    label: <Link to="/paid-companies">Paid Invoices</Link>,
  },
  {
    key: "/unpaid-companies",
    icon: <DollarCircleOutlined />,
    label: <Link to="/unpaid-companies">Unpaid Invoices</Link>,
  },
  {
    key: "/contact-requests",
    icon: <FormOutlined />,
    label: <Link to="/contact-requests">Contact Requests</Link>,
  },
  {
    key: "/quote-requests",
    icon: <AppstoreOutlined />,
    label: <Link to="/quote-requests">Quote Requests</Link>,
  },
];

export const Sidebar = () => {
  const user = useAppSelector(selectUser);
  const location = useLocation();

  return (
    <aside className="admin-sidebar">
      <div className="admin-sidebar-top">
        <LogoLockup size="sm" subtitle="Admin Console" />
        <Title level={5}>Navigation</Title>
        <Text>
          <UserOutlined /> {user?.username ?? "Guest"}
        </Text>
      </div>

      <Menu mode="inline" selectedKeys={[location.pathname]} items={items} />
    </aside>
  );
};
