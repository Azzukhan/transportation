import type { PropsWithChildren } from "react";

import "../../styles/admin-layout.css";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export const AppLayout = ({ children }: PropsWithChildren) => {
  return (
    <div className="admin-shell">
      <div className="admin-body">
        <Sidebar />
        <div className="admin-content">
          <Header />
          <main className="admin-main">{children}</main>
        </div>
      </div>
    </div>
  );
};
