import { motion } from "framer-motion";
import { HiOutlineDocumentReport, HiOutlineCheckCircle, HiOutlineClock, HiOutlineLocationMarker } from "react-icons/hi";
import{ HiOutlineCpuChip } from "react-icons/hi2";
import Card from "../components/Card";
import Badge from "../components/Badge";

const KPIS = [
  { label: "Total Reports", value: "1,284", icon: HiOutlineDocumentReport, tone: "blue" },
  { label: "Resolution Rate", value: "75%", icon: HiOutlineCheckCircle, tone: "green" },
  { label: "AI Accuracy", value: "94.6%", icon: HiOutlineCpuChip, tone: "amber" },
  { label: "Avg Response Time", value: "6.2 hrs", icon: HiOutlineClock, tone: "blue" },
];

const MONTHS = [
  { month: "Jan", value: 40 }, { month: "Feb", value: 55 }, { month: "Mar", value: 48 },
  { month: "Apr", value: 70 }, { month: "May", value: 62 }, { month: "Jun", value: 85 },
];

const CATEGORIES = [
  { label: "Potholes", value: 38, tone: "red" },
  { label: "Garbage", value: 27, tone: "amber" },
  { label: "Waterlogging", value: 19, tone: "blue" },
  { label: "Streetlights", value: 16, tone: "slate" },
];

const AI_PERFORMANCE = [
  { label: "Detection Confidence", value: 94 },
  { label: "False Positive Rate", value: 8 },
  { label: "Model Coverage", value: 89 },
];

const TOP_AREAS = [
  { area: "MG Road, Sector 12", count: 142 },
  { area: "Civil Lines", count: 118 },
  { area: "Ring Road West", count: 97 },
  { area: "Station Road", count: 81 },
];

const TRENDS = [
  { title: "Pothole reports up 18% this month", tone: "red" },
  { title: "Average resolution time improved by 1.4 hrs", tone: "green" },
  { title: "Waterlogging complaints spike during monsoon weeks", tone: "blue" },
];

const BAR_COLORS = { red: "bg-red-500", amber: "bg-amber-500", blue: "bg-blue-500", slate: "bg-slate-500" };

export default function Analytics() {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <header>
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">Citywide infrastructure performance and trends.</p>
      </header>

      <section className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {KPIS.map(({ label, value, icon: Icon, tone }) => (
          <motion.div key={label} whileHover={{ y: -4 }}>
            <Card className="border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
              <Icon size={22} className={`text-${tone}-500`} />
              <div className="mt-3 text-2xl font-bold">{value}</div>
              <div className="text-sm text-slate-500 dark:text-slate-400">{label}</div>
            </Card>
          </motion.div>
        ))}
      </section>

      <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md lg:col-span-2 dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">Monthly Overview</h2>
          <div className="mt-6 flex h-48 items-end gap-4">
            {MONTHS.map((m) => (
              <div key={m.month} className="flex flex-1 flex-col items-center gap-2">
                <motion.div
                  initial={{ height: 0 }}
                  whileInView={{ height: `${m.value}%` }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6 }}
                  className="w-full rounded-t-lg bg-gradient-to-t from-blue-500 to-blue-400"
                />
                <span className="text-xs text-slate-500 dark:text-slate-400">{m.month}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">Issue Category Summary</h2>
          <div className="mt-5 flex flex-col gap-4">
            {CATEGORIES.map((c) => (
              <div key={c.label}>
                <div className="flex justify-between text-sm">
                  <span>{c.label}</span>
                  <span className="font-medium">{c.value}%</span>
                </div>
                <div className="mt-1 h-2 w-full rounded-full bg-slate-200 dark:bg-slate-800">
                  <div className={`h-2 rounded-full ${BAR_COLORS[c.tone]}`} style={{ width: `${c.value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">AI Performance</h2>
          <div className="mt-5 flex flex-col gap-4">
            {AI_PERFORMANCE.map((p) => (
              <div key={p.label}>
                <div className="flex justify-between text-sm">
                  <span>{p.label}</span>
                  <span className="font-medium">{p.value}%</span>
                </div>
                <div className="mt-1 h-2 w-full rounded-full bg-slate-200 dark:bg-slate-800">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${p.value}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.7 }}
                    className="h-2 rounded-full bg-amber-500"
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">Top Affected Areas</h2>
          <ul className="mt-5 flex flex-col gap-3">
            {TOP_AREAS.map((a) => (
              <li key={a.area} className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <HiOutlineLocationMarker className="text-blue-500" />{a.area}
                </span>
                <span className="font-medium text-slate-500 dark:text-slate-400">{a.count}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">Recent Trends</h2>
          <ul className="mt-5 flex flex-col gap-3">
            {TRENDS.map((t) => (
              <li key={t.title} className="flex items-start gap-2 text-sm">
                <Badge tone={t.tone}>•</Badge>
                <span className="text-slate-600 dark:text-slate-300">{t.title}</span>
              </li>
            ))}
          </ul>
        </Card>
      </section>
    </motion.div>
  );
}