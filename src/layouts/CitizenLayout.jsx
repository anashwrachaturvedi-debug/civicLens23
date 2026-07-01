import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function CitizenLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900 dark:bg-[#0B1220] dark:text-slate-100">
      <Navbar />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 pt-20 pb-8 sm:px-6 sm:pt-24">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}