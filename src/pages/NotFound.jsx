import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { HiOutlineLocationMarker, HiOutlineHome, HiOutlineViewGrid } from "react-icons/hi";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-6 text-center text-slate-900 dark:bg-[#0B1220] dark:text-slate-100">
      <motion.div
        animate={{ y: [0, -12, 0] }}
        transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        className="flex h-24 w-24 items-center justify-center rounded-full bg-amber-500/10 text-amber-500"
      >
        <HiOutlineLocationMarker size={48} />
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="mt-6 text-7xl font-extrabold tracking-tight text-blue-500"
      >
        404
      </motion.h1>

      <motion.h2
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mt-4 text-2xl font-bold"
      >
        Oops! Page Not Found
      </motion.h2>

      <motion.p
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="mt-3 max-w-md text-slate-600 dark:text-slate-400"
      >
        The page you're looking for doesn't exist or has been moved.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="mt-8 flex flex-wrap items-center justify-center gap-4"
      >
        <Link to="/" className="flex items-center gap-2 rounded-lg bg-amber-500 px-6 py-3 font-semibold text-white hover:bg-amber-600">
          <HiOutlineHome /> Back to Home
        </Link>
        <Link to="/dashboard" className="flex items-center gap-2 rounded-lg border border-slate-300 px-6 py-3 font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800">
          <HiOutlineViewGrid /> Go to Dashboard
        </Link>
      </motion.div>
    </div>
  );
}