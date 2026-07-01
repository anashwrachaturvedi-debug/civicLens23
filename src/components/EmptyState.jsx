import React from "react";
import { FaDatabase } from "react-icons/fa";

const EmptyState = ({
  title = "No Data Available",
  message = "There's nothing to display at the moment. Once new reports are available, they'll appear here.",
  icon,
  primaryButtonText = "Refresh",
  secondaryButtonText = "Go Back",
  onPrimaryClick,
  onSecondaryClick,
  showButtons = true,
}) => {
  const Icon = icon || (
    <FaDatabase className="text-6xl text-blue-600 dark:text-blue-400" />
  );

  return (
    <section
      className="flex w-full items-center justify-center px-6 py-12"
      aria-labelledby="empty-state-title"
    >
      <div className="w-full max-w-xl rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-xl transition-all duration-300 hover:shadow-2xl dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-blue-50 shadow-md dark:bg-slate-800">
          {Icon}
        </div>

        <h2
          id="empty-state-title"
          className="text-2xl font-bold text-slate-900 dark:text-white"
        >
          {title}
        </h2>

        <p className="mx-auto mt-4 max-w-md leading-7 text-slate-600 dark:text-slate-400">
          {message}
        </p>

        {showButtons && (
          <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
            <button
              type="button"
              onClick={() => onPrimaryClick?.()}
              className="rounded-xl bg-blue-600 px-6 py-3 font-medium text-white shadow-md transition-all duration-200 hover:bg-blue-700 hover:shadow-lg active:scale-95 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900"
            >
              {primaryButtonText}
            </button>

            <button
              type="button"
              onClick={() => onSecondaryClick?.()}
              className="rounded-xl border border-slate-300 bg-white px-6 py-3 font-medium text-slate-700 shadow-sm transition-all duration-200 hover:border-slate-400 hover:bg-slate-100 active:scale-95 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 dark:focus:ring-offset-slate-900"
            >
              {secondaryButtonText}
            </button>
          </div>
        )}
      </div>
    </section>
  );
};

export default EmptyState;