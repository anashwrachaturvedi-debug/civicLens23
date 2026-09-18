import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { HiOutlineMenu, HiOutlineX } from "react-icons/hi";
import ThemeToggle from "./ThemeToggle";
import AshokaChakra from "./AshokaChakra";

const NAV_LINKS = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "Report Issue", to: "/report" },
  { label: "Analytics", to: "/analytics" },
  { label: "Live Map", to: "/map" },
  { label: "Settings", to: "/settings" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50">
      <div className="tricolor-strip" aria-hidden="true" />
      <div className="border-b border-slate-200/60 bg-white/70 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/70">
        <nav
          aria-label="Primary"
          className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8"
        >
          <Link
            to="/"
            className="flex items-center gap-2 rounded-lg text-lg font-bold tracking-tight focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-chakra-navy)]"
          >
            <AshokaChakra size={32} className="animate-chakra-spin" />
            <span>CivicLens AI</span>
          </Link>

          <div className="hidden items-center gap-1 lg:flex">
            {NAV_LINKS.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `rounded-lg px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-chakra-navy)] ${
                    isActive
                      ? "bg-orange-500/10 text-orange-600 dark:text-orange-400"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </div>

          <div className="hidden items-center gap-3 lg:flex">
            <ThemeToggle />
            <Link
              to="/report"
              className="rounded-lg px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-chakra-navy)] focus-visible:ring-offset-2"
              style={{ backgroundColor: "var(--color-flag-green)" }}
            >
              Report an Issue
            </Link>
          </div>

          <div className="flex items-center gap-2 lg:hidden">
            <ThemeToggle />
            <button
              type="button"
              aria-label={open ? "Close menu" : "Open menu"}
              aria-expanded={open}
              onClick={() => setOpen((v) => !v)}
              className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-chakra-navy)] dark:text-slate-300 dark:hover:bg-slate-800"
            >
              {open ? <HiOutlineX size={22} /> : <HiOutlineMenu size={22} />}
            </button>
          </div>
        </nav>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden border-t border-slate-200/60 bg-white/90 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/90 lg:hidden"
          >
            <div className="flex flex-col gap-1 px-6 py-4">
              {NAV_LINKS.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `rounded-lg px-4 py-3 text-sm font-medium ${
                      isActive
                        ? "bg-orange-500/10 text-orange-600 dark:text-orange-400"
                        : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                    }`
                  }
                >
                  {link.label}
                </NavLink>
              ))}
              <Link
                to="/report"
                onClick={() => setOpen(false)}
                className="mt-2 rounded-lg px-4 py-3 text-center text-sm font-semibold text-white"
                style={{ backgroundColor: "var(--color-flag-green)" }}
              >
                Report an Issue
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}