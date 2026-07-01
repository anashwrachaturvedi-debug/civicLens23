import { useState, useEffect } from "react";
import { NavLink, useLocation } from "react-router-dom";

const NAV_LINKS = {
  citizen: [
    { to: "/", label: "Home" },
    { to: "/report", label: "Report Issue" },
    { to: "/map", label: "Live Map" },
  ],
  authority: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/analytics", label: "Analytics" },
    { to: "/settings", label: "Settings" },
  ],
};

function usePortal() {
  const { pathname } = useLocation();
  const authorityRoutes = ["/dashboard", "/analytics", "/settings"];
  return authorityRoutes.some((r) => pathname.startsWith(r)) ? "authority" : "citizen";
}

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains("dark"));
  const portal = usePortal();
  const links = NAV_LINKS[portal];
  const { pathname } = useLocation();

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", handler);
    return () => window.removeEventListener("scroll", handler);
  }, []);

  useEffect(() => setMenuOpen(false), [pathname]);

  function toggleTheme() {
    const next = !isDark;
    setIsDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  }

  return (
    <nav
      className={`fixed inset-x-0 top-0 z-50 h-14 transition-all duration-200 ${
        scrolled
          ? "bg-white/95 shadow-sm backdrop-blur-sm dark:bg-slate-950/95"
          : "bg-white dark:bg-slate-950 border-b border-slate-100 dark:border-slate-800"
      }`}
      aria-label="Main navigation"
    >
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between gap-6 px-4 sm:px-6">
        <NavLink
          to={portal === "authority" ? "/dashboard" : "/"}
          className="flex items-center gap-2 shrink-0"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-white text-xs font-bold">
            CL
          </div>
          <span className="font-semibold text-slate-900 dark:text-white">
            CivicLens <span className="text-blue-600 dark:text-blue-400">AI</span>
          </span>
        </NavLink>

        <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1 text-[11px] font-medium uppercase tracking-widest text-blue-600 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-400">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-500" />
          {portal === "authority" ? "Authority" : "Citizen"}
        </span>

        <div className="hidden sm:flex items-center gap-6 ml-auto">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/" || to === "/dashboard"}
              className={({ isActive }) =>
                `text-sm font-medium transition-colors px-1 py-0.5 rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                  isActive
                    ? "text-blue-600 dark:text-blue-400"
                    : "text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-2 ml-4">
          <button
            onClick={toggleTheme}
            aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            {isDark ? (
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="1.5" />
                <path d="M8 1v1.5M8 13.5V15M1 8h1.5M13.5 8H15M3.05 3.05l1.06 1.06M11.9 11.9l1.06 1.06M3.05 12.95l1.06-1.06M11.9 4.1l1.06-1.06" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M13.5 9.5A6 6 0 016.5 2.5a6 6 0 100 11 6 6 0 007-4z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </button>

          <NavLink
            to={portal === "authority" ? "/" : "/dashboard"}
            className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-500 hover:border-blue-300 hover:text-blue-600 dark:border-slate-700 dark:text-slate-400 dark:hover:border-blue-700 dark:hover:text-blue-400 transition-colors"
          >
            {portal === "authority" ? "Citizen portal →" : "Authority →"}
          </NavLink>

          <button
            onClick={() => setMenuOpen((v) => !v)}
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
            className="sm:hidden flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            {menuOpen ? (
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {menuOpen && (
        <div className="sm:hidden border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-950 px-4 py-3 flex flex-col gap-1">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/" || to === "/dashboard"}
              className={({ isActive }) =>
                `block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400"
                    : "text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
          <div className="mt-2 pt-2 border-t border-slate-100 dark:border-slate-800">
            <NavLink
              to={portal === "authority" ? "/" : "/dashboard"}
              className="block px-3 py-2 rounded-lg text-sm text-slate-500 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800 transition-colors"
            >
              {portal === "authority" ? "Switch to citizen portal →" : "Switch to authority portal →"}
            </NavLink>
          </div>
        </div>
      )}
    </nav>
  );
}