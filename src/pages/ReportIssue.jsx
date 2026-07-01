import { useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { HiOutlineCloudUpload, HiOutlineLocationMarker, HiOutlinePhotograph } from "react-icons/hi";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Card from "../components/Card";

const CATEGORIES = ["Pothole", "Garbage Accumulation", "Waterlogging", "Damaged Road", "Broken Streetlight"];
const SEVERITIES = [
  { label: "Low", tone: "slate" },
  { label: "Medium", tone: "amber" },
  { label: "High", tone: "orange" },
  { label: "Critical", tone: "red" },
];

export default function ReportIssue() {
  const [severity, setSeverity] = useState("Medium");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-[#0B1220] dark:text-slate-100">
      <Navbar />
      <motion.main initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mx-auto max-w-4xl px-6 py-10">
        <header>
          <h1 className="text-2xl font-bold tracking-tight">Report an Issue</h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">Point, shoot, and submit. We'll take care of the rest.</p>
        </header>

        <form className="mt-8 flex flex-col gap-6">
          <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
            <h2 className="text-lg font-semibold">Upload Image</h2>
            <label className="mt-4 flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50/50 px-6 py-10 text-center transition-colors hover:border-blue-400 dark:border-slate-700 dark:bg-slate-900/40">
              <HiOutlineCloudUpload size={36} className="text-blue-500" />
              <span className="text-sm font-medium">Drag & drop a photo, or click to browse</span>
              <span className="text-xs text-slate-400">PNG or JPG, up to 10MB</span>
              <input type="file" accept="image/*" className="hidden" />
            </label>
            <div className="mt-4 flex h-40 w-full items-center justify-center rounded-lg border border-slate-200 bg-slate-100 text-slate-400 dark:border-slate-800 dark:bg-slate-800/40">
              <HiOutlinePhotograph size={32} />
              <span className="ml-2 text-sm">Image preview will appear here</span>
            </div>
          </Card>

          <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
            <h2 className="text-lg font-semibold">Location</h2>
            <div className="mt-4 flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-900/40">
              <HiOutlineLocationMarker className="text-blue-500" />
              GPS location will be auto-detected, or pin it on the map.
            </div>
          </Card>

          <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
            <h2 className="text-lg font-semibold">Issue Details</h2>
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-1 text-sm">
                Category
                <select className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900">
                  {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
                </select>
              </label>
              <fieldset className="flex flex-col gap-1 text-sm">
                <legend>Severity</legend>
                <div className="flex flex-wrap gap-2">
                  {SEVERITIES.map((s) => (
                    <button
                      type="button"
                      key={s.label}
                      onClick={() => setSeverity(s.label)}
                      className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${severity === s.label ? `border-${s.tone}-500 bg-${s.tone}-500/10 text-${s.tone}-600` : "border-slate-200 text-slate-500 dark:border-slate-700"}`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </fieldset>
            </div>
            <label className="mt-4 flex flex-col gap-1 text-sm">
              Description
              <textarea rows={4} placeholder="Describe the issue..." className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900" />
            </label>
          </Card>

          <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
            <h2 className="text-lg font-semibold">Contact Information</h2>
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <input placeholder="Full name" className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900" />
              <input placeholder="Phone number" className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900" />
            </div>
          </Card>

          <div className="flex flex-wrap gap-4">
            <Link to="/success" className="rounded-lg bg-amber-500 px-6 py-3 text-center font-semibold text-white hover:bg-amber-600">
              Submit Report
            </Link>
            <button type="reset" className="rounded-lg border border-slate-300 px-6 py-3 font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800">
              Reset
            </button>
          </div>
        </form>
      </motion.main>
      <Footer />
    </div>
  );
}