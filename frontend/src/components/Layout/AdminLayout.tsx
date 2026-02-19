import { useState } from "react";
import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";
import { Logo } from "@/components/Brand/Logo";
import {
  LayoutDashboard,
  Building2,
  Truck,
  Users,
  Wallet,
  FileText,
  HandCoins,
  Mail,
  MessageSquare,
  FilePlus2,
  Signature,
  LogOut,
  ChevronLeft,
  Menu,
  Sparkles,
} from "lucide-react";

const sidebarLinks = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Companies", path: "/companies", icon: Building2 },
  { label: "Trips", path: "/trips", icon: Truck },
  { label: "Driver Details", path: "/drivers", icon: Users },
  { label: "Driver Cash", path: "/driver-cash", icon: HandCoins },
  { label: "Employee Salaries", path: "/employee-salaries", icon: Wallet },
  { label: "Create Invoice", path: "/create-invoice", icon: FilePlus2 },
  { label: "Paid Invoices", path: "/paid-companies", icon: FileText },
  { label: "Unpaid Invoices", path: "/unpaid-companies", icon: FileText },
  { label: "Contact Requests", path: "/contact-requests", icon: Mail },
  { label: "Quote Requests", path: "/quote-requests", icon: MessageSquare },
  { label: "Signatories", path: "/signatories", icon: Signature },
];

export const AdminLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const pageTitle = sidebarLinks.find((l) => l.path === location.pathname)?.label ?? "Admin Workspace";

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const SidebarContent = ({ mobile = false }: { mobile?: boolean }) => (
    <div className="flex flex-col h-full bg-[linear-gradient(175deg,hsl(var(--sidebar-background))_0%,hsl(220_45%_10%)_100%)] text-sidebar-foreground">
      <div className="px-4 pt-5 pb-4 border-b border-sidebar-border/60">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center gap-2">
              <Logo size="sm" tone="light" />
              <span className="text-accent font-display font-bold text-xl leading-none">Port</span>
            </div>
          )}
          {!mobile && (
            <button
              onClick={() => setCollapsed((v) => !v)}
              className="hidden md:flex p-1.5 rounded-md hover:bg-sidebar-accent text-sidebar-foreground/70"
            >
              <ChevronLeft size={18} className={`transition-transform ${collapsed ? "rotate-180" : ""}`} />
            </button>
          )}
        </div>
      </div>

      <nav className="flex-1 px-3 py-5 space-y-1.5">
        {sidebarLinks.map((link) => {
          const active = location.pathname === link.path;
          return (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setMobileOpen(false)}
              className={`group relative flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all ${
                active
                  ? "bg-accent text-accent-foreground shadow-accent-glow"
                  : "text-sidebar-foreground/75 hover:text-sidebar-foreground hover:bg-sidebar-accent"
              }`}
            >
              <link.icon size={18} />
              {!collapsed && <span>{link.label}</span>}
              {active && !collapsed && (
                <Sparkles size={14} className="ml-auto text-accent-foreground/90" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto border-t border-sidebar-border/60 p-3 space-y-2">
        {!collapsed && user && (
          <div className="px-3 py-2 rounded-lg bg-sidebar-accent/70 border border-sidebar-border/50">
            <p className="text-[11px] uppercase tracking-wide text-sidebar-foreground/50">Signed In</p>
            <p className="text-sm truncate text-sidebar-foreground/90">{user.username}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent w-full transition-colors"
        >
          <LogOut size={18} />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-muted/30">
      <aside
        className={`hidden md:flex flex-col border-r border-sidebar-border/70 transition-all duration-300 ${
          collapsed ? "w-16" : "w-64"
        }`}
      >
        <SidebarContent />
      </aside>

      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.55 }}
              exit={{ opacity: 0 }}
              className="md:hidden fixed inset-0 bg-foreground z-40"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: "spring", damping: 24, stiffness: 260 }}
              className="md:hidden fixed left-0 top-0 bottom-0 w-64 z-50 border-r border-sidebar-border/70"
            >
              <SidebarContent mobile />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <div className="flex-1 flex flex-col min-h-screen">
        <header className="h-16 border-b border-border/60 bg-card/80 backdrop-blur-md px-4 md:px-6 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <button className="md:hidden p-1.5 rounded-md hover:bg-muted" onClick={() => setMobileOpen(true)}>
              <Menu size={20} />
            </button>
            <div>
              <p className="text-[11px] uppercase tracking-wider text-muted-foreground">Admin Workspace</p>
              <h2 className="font-display font-bold text-lg leading-tight">{pageTitle}</h2>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 rounded-full border border-border/70 bg-background px-3 py-1.5 text-xs text-muted-foreground">
            <Sparkles size={13} className="text-accent" />
            Sikar Cargo Operations
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6 overflow-auto bg-[radial-gradient(circle_at_top_right,hsl(var(--accent)/0.06),transparent_35%),radial-gradient(circle_at_bottom_left,hsl(var(--primary)/0.05),transparent_45%)]">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
