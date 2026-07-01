import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";

export default function AuthorityLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900 dark:bg-[#0B1220] dark:text-slate-100">
      <Navbar />
      <div className="mx-auto flex w-full max-w-7xl flex-1 pt-14">
        <aside className="hidden shrink-0 border-r border-slate-200 dark:border-slate-800 md:block">
          <Sidebar />
        </aside>
        <main className="flex-1 px-4 py-6 sm:px-6 sm:py-8">
          <Outlet />
        </main>
      </div>
      <Footer />
    </div>
  );
}