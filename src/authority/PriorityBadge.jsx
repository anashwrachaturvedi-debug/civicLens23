const PRIORITY_STYLES = {
  Critical: "bg-red-500/10 text-red-600 dark:text-red-400",
  High: "bg-orange-500/10 text-orange-600 dark:text-orange-400",
  Medium: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
  Low: "bg-slate-500/10 text-slate-600 dark:text-slate-400",
};

export default function PriorityBadge({ priority }) {
  const styles = PRIORITY_STYLES[priority] || PRIORITY_STYLES.Low;

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${styles}`}>
      {priority}
    </span>
  );
}