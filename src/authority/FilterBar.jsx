import { HiOutlineX } from "react-icons/hi";
import { ISSUE_CATEGORIES, ISSUE_PRIORITIES, ISSUE_STATUSES } from "../../utils/constants";

const SORT_OPTIONS = ["Newest First", "Oldest First", "Highest Severity", "Lowest Severity"];

export default function FilterBar({ filters, setFilters }) {
  function handleChange(field, value) {
    setFilters({ ...filters, [field]: value });
  }

  function handleClear() {
    setFilters({ category: "", priority: "", status: "", sort: "" });
  }

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-xl border border-slate-200/60 bg-white/70 p-4 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
      <label className="flex flex-col gap-1 text-xs">
        Category
        <select
          value={filters.category || ""}
          onChange={(event) => handleChange("category", event.target.value)}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
        >
          <option value="">All Categories</option>
          {ISSUE_CATEGORIES.map((category) => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1 text-xs">
        Priority
        <select
          value={filters.priority || ""}
          onChange={(event) => handleChange("priority", event.target.value)}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
        >
          <option value="">All Priorities</option>
          {ISSUE_PRIORITIES.map((priority) => (
            <option key={priority} value={priority}>{priority}</option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1 text-xs">
        Status
        <select
          value={filters.status || ""}
          onChange={(event) => handleChange("status", event.target.value)}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
        >
          <option value="">All Statuses</option>
          {ISSUE_STATUSES.map((status) => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1 text-xs">
        Sort By
        <select
          value={filters.sort || ""}
          onChange={(event) => handleChange("sort", event.target.value)}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
        >
          <option value="">Default</option>
          {SORT_OPTIONS.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </label>

      <button
        type="button"
        onClick={handleClear}
        className="ml-auto flex items-center gap-1 rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        <HiOutlineX size={16} /> Clear Filters
      </button>
    </div>
  );
}