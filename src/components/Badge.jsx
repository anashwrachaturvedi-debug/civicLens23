import React from "react";

const TONE_STYLES = {
  red: "bg-red-500/10 text-red-600 dark:text-red-400",
  orange: "bg-orange-500/10 text-orange-600 dark:text-orange-400",
  amber: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
  green: "bg-green-500/10 text-green-600 dark:text-green-400",
  blue: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  slate: "bg-slate-500/10 text-slate-600 dark:text-slate-400",
  primary: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  success: "bg-green-500/10 text-green-600 dark:text-green-400",
  warning: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
  danger: "bg-red-500/10 text-red-600 dark:text-red-400",
  info: "bg-sky-500/10 text-sky-600 dark:text-sky-400",
  neutral: "bg-gray-500/10 text-gray-600 dark:text-gray-400",
};

export default function Badge({ children, tone, variant, className = "" }) {
  const key = tone || variant || "slate";
  const styles = TONE_STYLES[key] || TONE_STYLES.slate;

  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${styles} ${className}`}
    >
      {children}
    </span>
  );
}