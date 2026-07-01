import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { HiOutlineCheckCircle } from "react-icons/hi";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Card from "../components/Card";
import Badge from "../components/Badge";

const DETAILS = [
  { label: "Issue ID", value: "CL-2042" },
  { label: "Submission Time", value: "Jun 30, 2026, 10:42 AM" },
  { label: "Estimated Resolution", value: "24–48 hours" },
];

export default function Success() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900 dark:bg-[#0B1220] dark:text-slate-100">
      <Navbar />
      <main className="mx-auto flex max-w-2xl flex-1 flex-col items-center justify-center px-6 py-16 text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 14 }}
          className="flex h-24 w-24 items-center justify-center rounded-full bg-green-500/10 text-green-500"
        >
          <HiOutlineCheckCircle size={52} />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="mt-6 text-3xl font-bold tracking-tight"
        >
          Report Submitted Successfully
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.25 }}
          className="mt-3 max-w-md text-slate-600 dark:text-slate-400"
        >
          Your infrastructure report has been received and forwarded to the appropriate municipal authority.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.35 }}
          className="mt-8 w-full"
        >
          <Card className="border border-slate-200/60 bg-white/70 p-6 text-left shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
            <div className="flex flex-col gap-3">
              {DETAILS.map((d) => (
                <div key={d.label} className="flex justify-between text-sm">
                  <span className="text-slate-500 dark:text-slate-400">{d.label}</span>
                  <span className="font-medium">{d.value}</span>
                </div>
              ))}
              <div className="flex justify-between text-sm">
                <span className="text-slate-500 dark:text-slate-400">Status</span>
                <Badge tone="amber">Pending</Badge>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.45 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-4"
        >
          <Link to="/report" className="rounded-lg bg-amber-500 px-5 py-3 font-semibold text-white hover:bg-amber-600">
            Report Another Issue
          </Link>
          <Link to="/dashboard" className="rounded-lg border border-slate-300 px-5 py-3 font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800">
            View Dashboard
          </Link>
          <Link to="/" className="rounded-lg px-5 py-3 font-semibold text-blue-500 hover:underline">
            Return Home
          </Link>
        </motion.div>
      </main>
      <Footer />
    </div>
  );
}