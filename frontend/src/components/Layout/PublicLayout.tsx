import { Outlet } from "react-router-dom";
import { PublicNavbar } from "./PublicNavbar";
import { Footer } from "./Footer";

export const PublicLayout = () => (
  <div className="min-h-screen flex flex-col">
    <PublicNavbar />
    <main className="flex-1 pt-16">
      <Outlet />
    </main>
    <Footer />
  </div>
);
