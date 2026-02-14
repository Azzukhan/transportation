import { Link } from "react-router-dom";
import { Logo } from "../Brand/Logo";
import { Mail, Phone, MapPin } from "lucide-react";

export const Footer = () => (
  <footer className="bg-primary text-primary-foreground">
    <div className="container mx-auto px-4 py-16">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
        <div className="space-y-4">
          <Logo size="lg" tone="light" />
          <p className="text-primary-foreground/70 text-sm leading-relaxed">
            Focused transport services for regular business movement and route-based cargo delivery.
          </p>
        </div>

        <div>
          <h4 className="font-display font-bold text-sm uppercase tracking-wider mb-4">Quick Links</h4>
          <ul className="space-y-2 text-sm">
            {[
              { label: "About Us", to: "/about" },
              { label: "Services", to: "/service" },
              { label: "Get a Quote", to: "/quote" },
              { label: "Contact", to: "/contact" },
            ].map((link) => (
              <li key={link.to}>
                <Link to={link.to} className="text-primary-foreground/60 hover:text-accent transition-colors">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="font-display font-bold text-sm uppercase tracking-wider mb-4">Services</h4>
          <ul className="space-y-2 text-sm text-primary-foreground/60">
            <li>1 Ton Pickup Service</li>
            <li>3 Ton Pickup Service</li>
            <li>7 Ton Service</li>
            <li>10 Ton Pickup Service</li>
            <li>Truck Freight</li>
            <li>Exhibition Logistics</li>
          </ul>
        </div>

        <div>
          <h4 className="font-display font-bold text-sm uppercase tracking-wider mb-4">Contact</h4>
          <ul className="space-y-3 text-sm text-primary-foreground/60">
            <li className="flex items-center gap-2"><Phone size={14} className="text-accent" /> +971 55 238 1722</li>
            <li className="flex items-center gap-2"><Phone size={14} className="text-accent" /> +971 55 251 6492</li>
            <li className="flex items-center gap-2"><Mail size={14} className="text-accent" /> Sikarcargo@gmail.com</li>
            <li className="flex items-center gap-2"><MapPin size={14} className="text-accent" /> G1 Office, Deira Naif, Dubai, UAE</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-primary-foreground/10 mt-12 pt-6 text-center text-xs text-primary-foreground/40">
        © {new Date().getFullYear()} Sikar Cargo. All rights reserved.
      </div>
    </div>
  </footer>
);
