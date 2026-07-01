import { HiOutlineX, HiOutlineLocationMarker, HiOutlineCalendar, HiOutlineUserGroup } from "react-icons/hi";
import PriorityBadge from "./PriorityBadge";
import StatusBadge from "./StatusBadge";

export default function IssueModal({ isOpen, onClose, issue }) {
  if (!isOpen || !issue) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="issue-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 px-4 backdrop-blur-sm"
    >
      <div className="relative w-full max-w-lg rounded-2xl border border-slate-200/60 bg-white p-6 shadow-xl dark:border-slate-800 dark:bg-slate-900">
        <button
          type="button"
          onClick={onClose}
          aria-label="Close issue details"
          className="absolute right-4 top-4 rounded-full p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800"
        >
          <HiOutlineX size={20} />
        </button>

        <img
          src={issue.image}
          alt={issue.title}
          className="h-48 w-full rounded-xl object-cover"
        />

        <h2 id="issue-modal-title" className="mt-4 text-lg font-bold tracking-tight">
          {issue.title}
        </h2>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <PriorityBadge priority={issue.priority} />
          <StatusBadge status={issue.status} />
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {issue.category}
          </span>
        </div>

        <p className="mt-4 text-sm text-slate-600 dark:text-slate-400">{issue.description}</p>

        <dl className="mt-5 flex flex-col gap-3 text-sm">
          <div className="flex items-center gap-2">
            <HiOutlineLocationMarker className="text-blue-500" />
            <dt className="sr-only">Location</dt>
            <dd>{issue.location}</dd>
          </div>
          <div className="flex items-center gap-2">
            <HiOutlineCalendar className="text-blue-500" />
            <dt className="sr-only">Reported Date</dt>
            <dd>{new Date(issue.reportedAt).toLocaleString()}</dd>
          </div>
          <div className="flex items-center gap-2">
            <HiOutlineUserGroup className="text-blue-500" />
            <dt className="sr-only">Assigned To</dt>
            <dd>{issue.assignedTo}</dd>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-800/50">
            <dt className="text-slate-500 dark:text-slate-400">Severity Score</dt>
            <dd className="font-semibold">{issue.severity}/100</dd>
          </div>
        </dl>

        <button
          type="button"
          onClick={onClose}
          className="mt-6 w-full rounded-lg bg-blue-500 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-600"
        >
          Close
        </button>
      </div>
    </div>
  );
}