import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  HiOutlineExclamationCircle,
  HiOutlineCheckCircle,
  HiOutlineChartBar,
  HiOutlineSearch,
  HiOutlineBell,
  HiOutlineMap,
  HiOutlineDocumentReport,
  HiOutlineCog,
  HiOutlineClipboardList,
} from "react-icons/hi";
import{ HiOutlineCpuChip } from "react-icons/hi2";
import Card from "../components/Card";
import Badge from "../components/Badge";

const STATS = [
  { label: "Total Issues", value: "1,284", trend: "+12%", icon: HiOutlineClipboardList, tone: "blue" },
  { label: "Critical Issues", value: "37", trend: "+4%", icon: HiOutlineExclamationCircle, tone: "red" },
  { label: "Resolved Issues", value: "962", trend: "+8%", icon: HiOutlineCheckCircle, tone: "green" },
  { label: "AI Accuracy", value: "94.6%", trend: "+1.2%", icon: HiOutlineCpuChip, tone: "amber" },
];

const ISSUES = [
  { id: "CL-2041", type: "Pothole", location: "MG Road, Sector 12", severity: "Critical", status: "Pending", date: "Jun 28, 2026" },
  { id: "CL-2040", type: "Waterlogging", location: "Civil Lines", severity: "High", status: "Assigned", date: "Jun 27, 2026" },
  { id: "CL-2039", type: "Garbage", location: "Park Street", severity: "Medium", status: "In Progress", date: "Jun 26, 2026" },
  { id: "CL-2038", type: "Streetlight", location: "Station Road", severity: "Low", status: "Resolved", date: "Jun 25, 2026" },
  { id: "CL-2037", type: "Pothole", location: "Ring Road West", severity: "High", status: "In Progress", date: "Jun 24, 2026" },
  { id: "CL-2036", type: "Damaged Road", location: "Sector 9 Market", severity: "Critical", status: "Pending", date: "Jun 23, 2026" },
];

const PRIORITY_QUEUE = [
  { title: "Large Pothole — Arterial Road", location: "MG Road, Sector 12", priority: "Critical" },
  { title: "Sewage Overflow", location: "Civil Lines", priority: "Critical" },
  { title: "Cracked Pavement", location: "Ring Road West", priority: "High" },
  { title: "Broken Streetlight Cluster", location: "Station Road", priority: "High" },
  { title: "Garbage Accumulation", location: "Park Street", priority: "Medium" },
];

const QUICK_ACTIONS = [
  { title: "View Map", desc: "See all issues plotted geographically.", icon: HiOutlineMap, to: "/map" },
  { title: "Analytics", desc: "Trends, hotspots, and efficiency reports.", icon: HiOutlineChartBar, to: "/analytics" },
  { title: "Reports", desc: "Generate monthly resolution reports.", icon: HiOutlineDocumentReport, to: "/reports" },
  { title: "Settings", desc: "Manage department and alert preferences.", icon: HiOutlineCog, to: "/settings" },
];

const AI_INSIGHTS = [
  { label: "AI Detection Accuracy", value: 95 },
  { label: "Resolution Prediction", value: 78 },
  { label: "Avg. Response Time Score", value: 62 },
  { label: "Most Affected Area Coverage", value: 41 },
];

const severityTone = { Critical: "red", High: "orange", Medium: "amber", Low: "slate" };
const statusTone = { Pending: "slate", Assigned: "blue", "In Progress": "amber", Resolved: "green" };
const today = new Date().toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

export default function Dashboard() {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <header className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">Welcome back — here's what's happening across the city today.</p>
          <p className="text-xs text-slate-400">{today}</p>
        </div>
        <div className="flex items-center gap-3">
          <label className="relative">
            <span className="sr-only">Search issues</span>
            <HiOutlineSearch className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input type="search" placeholder="Search issues, locations..." className="w-56 rounded-lg border border-slate-200 bg-white/70 py-2 pl-10 pr-3 text-sm backdrop-blur focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900/60" />
          </label>
          <button aria-label="Notifications" className="relative rounded-full p-2 hover:bg-slate-100 dark:hover:bg-slate-800">
            <HiOutlineBell size={20} />
            <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
          </button>
          <div aria-label="Profile" className="h-9 w-9 rounded-full bg-gradient-to-br from-blue-500 to-blue-700" />
        </div>
      </header>

      <section aria-label="Statistics" className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {STATS.map(({ label, value, trend, icon: Icon, tone }) => (
          <motion.div key={label} whileHover={{ y: -4 }} transition={{ duration: 0.2 }}>
            <Card className={`border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50`}>
              <div className="flex items-center justify-between">
                <Icon size={24} className={`text-${tone}-500`} />
                <Badge tone={tone}>{trend}</Badge>
              </div>
              <div className="mt-4 text-2xl font-bold">{value}</div>
              <div className="text-sm text-slate-500 dark:text-slate-400">{label}</div>
            </Card>
          </motion.div>
        ))}
      </section>

      <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ duration: 0.4 }} className="lg:col-span-2">
          <Card className="border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
            <h2 className="text-lg font-semibold">Recent Issues</h2>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[560px] text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 dark:border-slate-800">
                    {["ID", "Type", "Location", "Severity", "Status", "Reported"].map((h) => (
                      <th key={h} scope="col" className="py-2 pr-4 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ISSUES.map((issue) => (
                    <tr key={issue.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-800/60 dark:hover:bg-slate-800/40">
                      <td className="py-3 pr-4 font-medium">{issue.id}</td>
                      <td className="py-3 pr-4">{issue.type}</td>
                      <td className="py-3 pr-4 text-slate-500 dark:text-slate-400">{issue.location}</td>
                      <td className="py-3 pr-4"><Badge tone={severityTone[issue.severity]}>{issue.severity}</Badge></td>
                      <td className="py-3 pr-4"><Badge tone={statusTone[issue.status]}>{issue.status}</Badge></td>
                      <td className="py-3 pr-4 text-slate-500 dark:text-slate-400">{issue.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </motion.div>

        <Card className="border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">Priority Queue</h2>
          <ul className="mt-4 flex flex-col gap-3">
            {PRIORITY_QUEUE.map((item) => (
              <li key={item.title} className="flex items-start justify-between gap-3 rounded-lg border border-slate-100 p-3 dark:border-slate-800">
                <div>
                  <p className="text-sm font-medium">{item.title}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{item.location}</p>
                </div>
                <Badge tone={severityTone[item.priority]}>{item.priority}</Badge>
              </li>
            ))}
          </ul>
        </Card>
      </section>

      <section aria-label="Quick Actions" className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {QUICK_ACTIONS.map(({ title, desc, icon: Icon, to }) => (
          <motion.div key={title} whileHover={{ y: -4 }} transition={{ duration: 0.2 }}>
            <Link to={to} className="block h-full rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500">
              <Card className="h-full border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
                <Icon size={22} className="text-blue-500" />
                <h3 className="mt-3 text-sm font-semibold">{title}</h3>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{desc}</p>
              </Card>
            </Link>
          </motion.div>
        ))}
      </section>

      <section className="mt-8">
        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">AI Insights</h2>
          <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2">
            {AI_INSIGHTS.map(({ label, value }) => (
              <div key={label}>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600 dark:text-slate-300">{label}</span>
                  <span className="font-semibold">{value}%</span>
                </div>
                <div className="mt-2 h-2 w-full rounded-full bg-slate-200 dark:bg-slate-800">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${value}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="h-2 rounded-full bg-blue-500"
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </motion.div>
  );
}