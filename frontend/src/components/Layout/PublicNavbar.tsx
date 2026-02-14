import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import { Logo } from "../Brand/Logo";
import { Button } from "@/components/ui/button";

const navLinks = [
  { label: "Home", path: "/" },
  { label: "About", path: "/about" },
  { label: "Services", path: "/service" },
  { label: "Live Ops", path: "/live-operations" },
  { label: "Contact", path: "/contact" },
];

export const PublicNavbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass">
      <div className="container mx-auto flex items-center justify-between h-16 px-4">
        <Link to="/">
          <Logo />
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                location.pathname === link.path
                  ? "text-accent font-semibold"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <Link to="/quote">
            <Button className="bg-accent-gradient text-accent-foreground shadow-accent-glow hover:opacity-90 border-0">
              Get a Quote
            </Button>
          </Link>
          <Link to="/login">
            <Button variant="outline" size="sm">
              Admin Login
            </Button>
          </Link>
        </div>

        {/* Mobile toggle */}
        <button className="md:hidden p-2" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass border-t border-border overflow-hidden"
          >
            <nav className="flex flex-col p-4 gap-2">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMobileOpen(false)}
                  className={`px-4 py-3 rounded-md text-sm font-medium ${
                    location.pathname === link.path
                      ? "text-accent bg-accent/10"
                      : "text-muted-foreground"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
              <Link to="/quote" onClick={() => setMobileOpen(false)}>
                <Button className="w-full bg-accent-gradient text-accent-foreground border-0 mt-2">
                  Get a Quote
                </Button>
              </Link>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};
