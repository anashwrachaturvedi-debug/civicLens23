const STATUS_STYLES = {
  Pending: "bg-slate-500/10 text-slate-600 dark:text-slate-400",
  Assigned: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  "In Progress": "bg-amber-500/10 text-amber-600 dark:text-amber-400",
  Resolved: "bg-green-500/10 text-green-600 dark:text-green-400",
};

export default function StatusBadge({ status }) {
  const styles = STATUS_STYLES[status] || STATUS_STYLES.Pending;

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${styles}`}>
      {status}
    </span>
  );
}