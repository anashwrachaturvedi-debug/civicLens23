// src/pages/Home.jsx
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  HiOutlineCpuChip as HiCpu,
} from "react-icons/hi2";
import {
  HiOutlineChartBar,
  HiOutlineMap,
  HiOutlineArrowRight,
} from "react-icons/hi";
import Card from "../components/Card";

const STATS = [
  { label: "Issues Detected", value: "1,284+" },
  { label: "AI Accuracy", value: "94.6%" },
  { label: "Avg. Response Time", value: "6.2 hrs" },
];

const FEATURES = [
  {
    title: "AI Detection",
    desc: "Automatically detect potholes, garbage, broken streetlights and flooding using computer vision.",
    icon: HiCpu,
  },
  {
    title: "Severity Scoring",
    desc: "Every issue is automatically scored and prioritized so authorities know what to fix first.",
    icon: HiOutlineChartBar,
  },
  {
    title: "Live City Map",
    desc: "GPS-tagged issues appear instantly on a real-time interactive map for full visibility.",
    icon: HiOutlineMap,
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-[#0B1220] dark:text-slate-100">
    

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden">
          <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-blue-400/30 blur-3xl" />
            <div className="absolute -right-24 top-40 h-80 w-80 rounded-full bg-blue-300/30 blur-3xl" />
            <div className="absolute inset-0 bg-gradient-to-b from-blue-50/60 via-transparent to-transparent dark:from-blue-500/10" />
          </div>

          <div className="mx-auto max-w-5xl px-6 py-24 text-center lg:py-32">
            <motion.h1
              initial="hidden"
              animate="show"
              variants={fadeUp}
              transition={{ duration: 0.5 }}
              className="text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl lg:text-6xl"
            >
              Fixing cities before
              <span className="bg-gradient-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent"> citizens complain.</span>
            </motion.h1>

            <motion.p
              initial="hidden"
              animate="show"
              variants={fadeUp}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="mx-auto mt-6 max-w-2xl text-lg text-slate-600 dark:text-slate-300"
            >
              CivicLens AI detects potholes, garbage, flooding and other urban
              infrastructure problems using AI, and instantly alerts the right
              authorities to act.
            </motion.p>

            <motion.div
              initial="hidden"
              animate="show"
              variants={fadeUp}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-10 flex flex-wrap items-center justify-center gap-4"
            >
              <Link
                to="/report"
                className="flex items-center gap-2 rounded-xl bg-blue-600 px-7 py-3.5 font-semibold text-white shadow-sm transition-colors hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              >
                Report an Issue
                <HiOutlineArrowRight />
              </Link>
              <Link
                to="/dashboard"
                className="rounded-xl border border-slate-300 px-7 py-3.5 font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              >
                Live Dashboard
              </Link>
            </motion.div>

            <motion.div
              initial="hidden"
              animate="show"
              variants={fadeUp}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-4 sm:grid-cols-3"
            >
              {STATS.map((s) => (
                <Card key={s.label} className="p-5">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{s.value}</div>
                  <div className="mt-1 text-sm text-slate-500 dark:text-slate-400">{s.label}</div>
                </Card>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="mx-auto max-w-7xl px-6 py-20 lg:py-28">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything authorities need
            </h2>
            <p className="mt-4 text-slate-600 dark:text-slate-400">
              A single platform to detect, prioritize, and resolve infrastructure
              issues across the city.
            </p>
          </div>

          <div className="mt-14 grid grid-cols-1 gap-6 md:grid-cols-3">
            {FEATURES.map(({ title, desc, icon: Icon }, i) => (
              <motion.div
                key={title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <Card className="h-full p-8">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400">
                    <Icon size={24} />
                  </div>
                  <h3 className="mt-5 text-xl font-semibold">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                    {desc}
                  </p>
                </Card>
              </motion.div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="border-t border-slate-200/60 bg-white py-20 dark:border-slate-800 dark:bg-slate-950 lg:py-28">
          <div className="mx-auto max-w-3xl px-6 text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Ready to improve your city?
            </h2>
            <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">
              Join citizens and city departments making urban infrastructure
              smarter, faster, and more responsive.
            </p>
            <Link
              to="/report"
              className="mt-10 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-8 py-4 font-semibold text-white shadow-sm transition-colors hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
            >
              Get Started
              <HiOutlineArrowRight />
            </Link>
          </div>
        </section>
      </main>

  
    </div>
  );
}