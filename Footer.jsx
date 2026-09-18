import { Link } from "react-router-dom";
import AshokaChakra from "./AshokaChakra";

const FOOTER_LINKS = [
  {
    heading: "Product",
    links: [
      { label: "Dashboard", to: "/dashboard" },
      { label: "Live Map", to: "/map" },
      { label: "Analytics", to: "/analytics" },
      { label: "Report an Issue", to: "/report" },
    ],
  },
  {
    heading: "Platform",
    links: [
      { label: "Settings", to: "/settings" },
      { label: "How it works", to: "/#features" },
    ],
  },
];

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-slate-200/60 bg-white text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-4">
          <div className="sm:col-span-2 lg:col-span-2">
            <Link to="/" className="flex items-center gap-2 text-lg font-bold text-slate-900 dark:text-white">
              <AshokaChakra size={28} />
              CivicLens AI
            </Link>
            <p className="mt-4 max-w-sm text-sm leading-relaxed">
              AI-powered urban infrastructure monitoring that helps cities detect
              and resolve civic issues before residents have to report them.
            </p>
          </div>

          {FOOTER_LINKS.map((col) => (
            <div key={col.heading}>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{col.heading}</h3>
              <ul className="mt-4 flex flex-col gap-3">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <Link to={link.to} className="text-sm transition-colors hover:text-orange-600 dark:hover:text-orange-400">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col gap-4 border-t border-slate-200/60 pt-8 text-sm dark:border-slate-800 sm:flex-row sm:items-center sm:justify-between">
          <p>© {year} CivicLens AI. All rights reserved.</p>
          <div className="flex gap-6">
            <Link to="/settings" className="hover:text-orange-600 dark:hover:text-orange-400">Privacy</Link>
            <Link to="/settings" className="hover:text-green-700 dark:hover:text-green-400">Terms</Link>
          </div>
        </div>
      </div>
      <div className="tricolor-strip" aria-hidden="true" />
    </footer>
  );
}