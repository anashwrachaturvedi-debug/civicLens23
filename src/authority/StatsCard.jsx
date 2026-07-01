import { HiOutlineArrowUp, HiOutlineArrowDown } from "react-icons/hi";

export default function StatsCard({ title, value, icon: Icon, trend, color = "blue" }) {
  const isPositive = typeof trend === "string" ? trend.startsWith("+") : trend >= 0;

  return (
    <div className="rounded-2xl border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md transition-shadow hover:shadow-md dark:border-slate-800 dark:bg-slate-900/50">
      <div className="flex items-center justify-between">
        {Icon && <Icon size={24} className={`text-${color}-500`} />}
        {trend && (
          <span
            className={`flex items-center gap-1 text-xs font-semibold ${
              isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
            }`}
          >
            {isPositive ? <HiOutlineArrowUp size={14} /> : <HiOutlineArrowDown size={14} />}
            {trend}
          </span>
        )}
      </div>
      <div className="mt-4 text-2xl font-bold">{value}</div>
      <div className="text-sm text-slate-500 dark:text-slate-400">{title}</div>
    </div>
  );
}