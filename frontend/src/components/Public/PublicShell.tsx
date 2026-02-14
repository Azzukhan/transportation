import {
  EnvironmentOutlined,
  MailOutlined,
  MenuOutlined,
  PhoneOutlined,
  PlayCircleOutlined,
} from "@ant-design/icons";
import { Button, Drawer, Space } from "antd";
import { useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

import { LogoLockup } from "../Brand/LogoLockup";
import "../../styles/public-shell.css";

const navItems = [
  { to: "/", label: "Home" },
  { to: "/service", label: "Services" },
  { to: "/about", label: "About Us" },
  { to: "/feature", label: "Why Us" },
  { to: "/quote", label: "Get Quote" },
  { to: "/live-operations", label: "Live Operations" },
  { to: "/contact", label: "Contact" },
];

export const PublicShell = () => {
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const isActive = (to: string) =>
    location.pathname === to || (to === "/service" && location.pathname.startsWith("/service/"));

  return (
    <div className="public-shell">
      <div className="bg-orb bg-orb-1" aria-hidden="true" />
      <div className="bg-orb bg-orb-2" aria-hidden="true" />

      <header className="public-header-wrap">
        <div className="public-topbar">
          <div className="public-topbar-inner">
            <div className="public-topbar-left">
              <a href="tel:+971552381722"><PhoneOutlined /> +971 55 238 1722</a>
              <a href="mailto:Sikarcargo@gmail.com"><MailOutlined /> Sikarcargo@gmail.com</a>
              <span><EnvironmentOutlined /> Deira Naif, Dubai, UAE</span>
            </div>
            <Link to="/live-operations" className="public-topbar-track">
              <PlayCircleOutlined /> Live Operations
            </Link>
          </div>
        </div>

        <nav className="public-nav">
          <div className="public-nav-inner">
            <Link to="/" className="public-brand" aria-label="Sikar Cargo Home">
              <LogoLockup size="md" />
            </Link>

            <div className="public-nav-links">
              {navItems.map((item) => (
                <Link key={item.to} to={item.to} className={isActive(item.to) ? "active" : ""}>
                  {item.label}
                </Link>
              ))}
            </div>

            <Space>
              <Link to="/quote">
                <Button type="primary">Quick Quote</Button>
              </Link>
              <Link to="/login">
                <Button>Admin Login</Button>
              </Link>
              <Button className="mobile-nav-btn" icon={<MenuOutlined />} onClick={() => setOpen(true)} />
            </Space>
          </div>
        </nav>
      </header>

      <Drawer placement="right" onClose={() => setOpen(false)} open={open} width={290}>
        <div className="mobile-nav-list">
          {navItems.map((item) => (
            <Link key={item.to} to={item.to} onClick={() => setOpen(false)}>
              {item.label}
            </Link>
          ))}
          <Link to="/login" onClick={() => setOpen(false)}>
            Admin Login
          </Link>
        </div>
      </Drawer>

      <Outlet />

      <footer className="public-footer">
        <div className="public-footer-grid">
          <div>
            <h4>Sikar Cargo Transport</h4>
            <p>
              Trusted cargo transport services across UAE for pickups, truck freight, and exhibition
              material transfer schedules.
            </p>
          </div>
          <div>
            <h4>Contact</h4>
            <p>G1 Office, Deira Naif, Dubai, UAE</p>
            <p>+971 55 238 1722</p>
            <p>+971 55 251 6492</p>
            <p>Sikarcargo@gmail.com</p>
          </div>
          <div>
            <h4>Explore</h4>
            <p><Link to="/service">Transport Services</Link></p>
            <p><Link to="/live-operations">Work Gallery</Link></p>
            <p><Link to="/quote">Request Quotation</Link></p>
            <p><Link to="/contact">Contact Operations</Link></p>
          </div>
        </div>
      </footer>
    </div>
  );
};
