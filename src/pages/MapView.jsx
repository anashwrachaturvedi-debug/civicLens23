import { useState } from "react";
import { motion } from "framer-motion";
import { HiOutlineSearch, HiOutlineFilter, HiOutlineLocationMarker, HiOutlineMap } from "react-icons/hi";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import Card from "../components/Card";
import Badge from "../components/Badge";

const LEGEND = [
  { label: "Critical", tone: "red" },
  { label: "High", tone: "orange" },
  { label: "Medium", tone: "amber" },
  { label: "Low", tone: "slate" },
];

const LIVE_STATS = [
  { label: "Active Issues", value: "1,284" },
  { label: "Critical Now", value: "37" },
  { label: "Resolved Today", value: "52" },
];

const NEARBY_ISSUES = [
  { id: "CL-2041", type: "Pothole", location: "MG Road, Sector 12", priority: "Critical" },
  { id: "CL-2040", type: "Waterlogging", location: "Civil Lines", priority: "High" },
  { id: "CL-2039", type: "Garbage", location: "Park Street", priority: "Medium" },
  { id: "CL-2038", type: "Streetlight", location: "Station Road", priority: "Low" },
  { id: "CL-2037", type: "Pothole", location: "Ring Road West", priority: "High" },
];

const priorityTone = { Critical: "red", High: "orange", Medium: "amber", Low: "slate" };

export default function MapView() {
  const [selected, setSelected] = useState(NEARBY_ISSUES[0]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-[#0B1220] dark:text-slate-100">
      <Navbar />
      <div className="mx-auto flex max-w-7xl">
        <Sidebar />
        <motion.main initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="flex-1 px-6 py-8">
          <header className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Live Monitoring</h1>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">Real-time geospatial view of city infrastructure issues.</p>
            </div>
            <div className="flex items-center gap-3">
              <label className="relative">
                <span className="sr-only">Search location</span>
                <HiOutlineSearch className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input type="search" placeholder="Search location..." className="w-52 rounded-lg border border-slate-200 bg-white/70 py-2 pl-10 pr-3 text-sm backdrop-blur focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900/60" />
              </label>
              <button className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white/70 px-3 py-2 text-sm dark:border-slate-800 dark:bg-slate-900/60">
                <HiOutlineFilter /> Filter
              </button>
            </div>
          </header>

          <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <Card className="relative flex h-[420px] items-center justify-center overflow-hidden border border-slate-200/60 bg-white/70 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
                <div className="text-center text-slate-400">
                  <HiOutlineMap size={56} className="mx-auto mb-3" />
                  <p className="text-sm">Interactive city map renders here</p>
                </div>
                <div className="absolute bottom-4 left-4 flex gap-3 rounded-lg bg-white/80 p-3 backdrop-blur dark:bg-slate-900/70">
                  {LEGEND.map((l) => (
                    <span key={l.label} className="flex items-center gap-1 text-xs">
                      <span className={`h-2 w-2 rounded-full bg-${l.tone}-500`} />
                      {l.label}
                    </span>
                  ))}
                </div>
              </Card>

              <section className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
                {LIVE_STATS.map((s) => (
                  <Card key={s.label} className="border border-slate-200/60 bg-white/70 p-5 text-center shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
                    <div className="text-xl font-bold">{s.value}</div>
                    <div className="text-sm text-slate-500 dark:text-slate-400">{s.label}</div>
                  </Card>
                ))}
              </section>
            </div>

            <div className="flex flex-col gap-6">
              <Card className="border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
                <h2 className="text-lg font-semibold">Nearby Issues</h2>
                <ul className="mt-4 flex flex-col gap-3">
                  {NEARBY_ISSUES.map((issue) => (
                    <li key={issue.id}>
                      <button
                        onClick={() => setSelected(issue)}
                        className={`flex w-full items-center justify-between rounded-lg border p-3 text-left text-sm transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/40 ${selected.id === issue.id ? "border-blue-400" : "border-slate-100 dark:border-slate-800"}`}
                      >
                        <span>
                          <span className="block font-medium">{issue.type}</span>
                          <span className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400"><HiOutlineLocationMarker />{issue.location}</span>
                        </span>
                        <Badge tone={priorityTone[issue.priority]}>{issue.priority}</Badge>
                      </button>
                    </li>
                  ))}
                </ul>
              </Card>

              <Card className="border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
                <h2 className="text-lg font-semibold">Selected Issue</h2>
                <div className="mt-4 text-sm">
                  <p className="font-medium">{selected.id} — {selected.type}</p>
                  <p className="mt-1 flex items-center gap-1 text-slate-500 dark:text-slate-400"><HiOutlineLocationMarker />{selected.location}</p>
                  <div className="mt-3"><Badge tone={priorityTone[selected.priority]}>{selected.priority}</Badge></div>
                </div>
              </Card>
            </div>
          </section>
        </motion.main>
      </div>
      <Footer />
    </div>
  );
}