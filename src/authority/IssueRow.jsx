import PriorityBadge from "./PriorityBadge";
import StatusBadge from "./StatusBadge";

export default function IssueRow({ issue, onView }) {
  return (
    <tr className="border-b border-slate-100 transition-colors last:border-0 hover:bg-slate-50 dark:border-slate-800/60 dark:hover:bg-slate-800/40">
      <td className="py-3 pr-4 font-medium">{issue.id}</td>
      <td className="py-3 pr-4">{issue.title}</td>
      <td className="py-3 pr-4 text-slate-500 dark:text-slate-400">{issue.category}</td>
      <td className="py-3 pr-4"><PriorityBadge priority={issue.priority} /></td>
      <td className="py-3 pr-4"><StatusBadge status={issue.status} /></td>
      <td className="py-3 pr-4 text-slate-500 dark:text-slate-400">{issue.location}</td>
      <td className="py-3 pr-4 text-slate-500 dark:text-slate-400">
        {new Date(issue.reportedAt).toLocaleDateString()}
      </td>
      <td className="py-3 pr-4">
        <button
          type="button"
          onClick={() => onView(issue)}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-600 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          View Details
        </button>
      </td>
    </tr>
  );
}