import React from "react";

const Loader = ({
  size = "md",
  message = "Analyzing Urban Infrastructure...",
  fullScreen = false,
}) => {
  const spinnerSizes = {
    sm: "h-10 w-10 border-[3px]",
    md: "h-14 w-14 border-4",
    lg: "h-20 w-20 border-[5px]",
  };

  return (
    <div
      className={`${
        fullScreen ? "fixed inset-0 z-50" : "w-full h-full min-h-[320px]"
      } flex items-center justify-center bg-white/80 dark:bg-slate-950/80 backdrop-blur-sm transition-colors duration-300`}
    >
      <div className="flex flex-col items-center rounded-3xl border border-slate-200/70 bg-white/80 px-8 py-10 shadow-2xl backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/80 animate-pulse">
        <div
          className={`${spinnerSizes[size] || spinnerSizes.md} rounded-full border-slate-300 border-t-blue-600 dark:border-slate-700 dark:border-t-blue-400 animate-spin shadow-lg`}
        />

        <div className="mt-6 text-center">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            CivicLens AI
          </h2>

          <p className="mt-3 text-base font-medium text-slate-700 dark:text-slate-200">
            {message}
          </p>

          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            Please wait while AI processes your request.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Loader;