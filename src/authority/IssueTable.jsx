import IssueRow from "./IssueRow";

const COLUMNS = ["ID", "Title", "Category", "Priority", "Status", "Location", "Reported", "Actions"];

export default function IssueTable({ issues, onViewIssue }) {
  if (!issues?.length) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 py-16 text-center text-slate-400 dark:border-slate-700">
        <p className="text-sm font-medium">No issues found</p>
        <p className="mt-1 text-xs">Try adjusting your filters or search query.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200/60 bg-white/70 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
      <table className="w-full min-w-[720px] text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-slate-500 dark:border-slate-800">
            {COLUMNS.map((column) => (
              <th key={column} scope="col" className="px-4 py-3 font-medium">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {issues.map((issue) => (
            <IssueRow key={issue.id} issue={issue} onView={onViewIssue} />
          ))}
        </tbody>
      </table>
    </div>
  );
}