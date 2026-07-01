import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  {
    label: "Dashboard",
    to: "/dashboard",
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <rect x="1.5" y="1.5" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
        <rect x="10.5" y="1.5" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
        <rect x="1.5" y="10.5" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
        <rect x="10.5" y="10.5" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
      </svg>
    ),
  },
  {
    label: "Analytics",
    to: "/analytics",
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <path d="M2 14l4-4 3 3 4-5 3 2" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M2 16h14" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    label: "Settings",
    to: "/settings",
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <circle cx="9" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.4" />
        <path d="M9 1.5v1.8M9 14.7v1.8M1.5 9h1.8M14.7 9h1.8M3.7 3.7l1.27 1.27M13.03 13.03l1.27 1.27M14.3 3.7l-1.27 1.27M4.97 13.03l-1.27 1.27" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      </svg>
    ),
  },
];

const STAT_PILLS = [
  { label: "Open", value: 24, color: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950" },
  { label: "Critical", value: 6, color: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950" },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const { pathname } = useLocation();

  const linkBase =
    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 group";
  const linkActive =
    "bg-blue-600 text-white shadow-sm";
  const linkIdle =
    "text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100";

  return (
    <aside
      className={`
        hidden sm:flex flex-col shrink-0 h-screen sticky top-0
        border-r border-gray-100 dark:border-gray-800
        bg-white dark:bg-gray-950
        transition-all duration-200 ease-in-out
        ${collapsed ? "w-[60px]" : "w-[220px]"}
      `}
      aria-label="Authority navigation"
    >
      {/* Top spacer — aligns with Navbar height */}
      <div className="h-14 shrink-0" />

      {/* Nav items */}
      <nav className="flex-1 flex flex-col gap-0.5 px-2 pt-3 overflow-y-auto">
        {NAV_ITEMS.map(({ label, to, icon }) => {
          const isActive = pathname === to || (to !== "/dashboard" && pathname.startsWith(to));
          return (
            <NavLink
              key={to}
              to={to}
              className={`${linkBase} ${isActive ? linkActive : linkIdle}`}
              title={collapsed ? label : undefined}
            >
              <span className="shrink-0">{icon}</span>
              {!collapsed && <span className="truncate">{label}</span>}
            </NavLink>
          );
        })}

        {/* Divider */}
        <div className="my-3 border-t border-gray-100 dark:border-gray-800" />

        {/* Quick stats — only when expanded */}
        {!collapsed && (
          <div className="px-1 pb-2">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-600 mb-2 px-2">
              Live status
            </p>
            <div className="flex flex-col gap-1">
              {STAT_PILLS.map(({ label, value, color }) => (
                <div
                  key={label}
                  className={`flex items-center justify-between px-3 py-1.5 rounded-lg text-xs font-medium ${color}`}
                >
                  <span>{label}</span>
                  <span className="font-semibold tabular-nums">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Switch to citizen portal */}
      {!collapsed && (
        <div className="px-2 pb-3">
          <NavLink
            to="/"
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-gray-400 dark:text-gray-600 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <path d="M6 10L3 7l3-3M11 7H3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Citizen portal
          </NavLink>
        </div>
      )}

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed((v) => !v)}
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        className="mx-2 mb-4 flex items-center justify-center h-8 rounded-lg text-gray-400 dark:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-300 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 14 14"
          fill="none"
          aria-hidden="true"
          className={`transition-transform duration-200 ${collapsed ? "rotate-180" : ""}`}
        >
          <path d="M9 2L4 7l5 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        {!collapsed && <span className="ml-2 text-xs">Collapse</span>}
      </button>
    </aside>
  );
}