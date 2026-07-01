import { useState } from "react";
import { motion } from "framer-motion";
import Card from "../components/Card";

const THEMES = ["Blue", "Slate", "Amber"];

function Toggle({ checked, onChange, label }) {
  return (
    <label className="flex cursor-pointer items-center justify-between gap-4 py-2">
      <span className="text-sm">{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={onChange}
        className={`relative h-6 w-11 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
          checked ? "bg-blue-500" : "bg-slate-300 dark:bg-slate-700"
        }`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
            checked ? "translate-x-5" : "translate-x-0.5"
          }`}
        />
      </button>
    </label>
  );
}

export default function Settings() {
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState({ email: true, push: true, sms: false });
  const [twoFactor, setTwoFactor] = useState(false);
  const [saved, setSaved] = useState(false);

  function handleSave() {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <header>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">Manage your account, preferences, and security.</p>
      </header>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">Profile</h2>
          <div className="mt-4 flex flex-col gap-3">
            <input
              defaultValue="Aarav Sharma"
              aria-label="Full name"
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
            />
            <input
              defaultValue="aarav.sharma@civiclens.ai"
              aria-label="Email address"
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
            />
            <input
              defaultValue="+91 98765 43210"
              aria-label="Phone number"
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
            />
          </div>
        </Card>

        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">Appearance</h2>
          <div className="mt-2">
            <Toggle
              checked={darkMode}
              onChange={() => setDarkMode(!darkMode)}
              label="Dark Mode"
            />
          </div>
          <div className="mt-3">
            <p className="text-sm font-medium">Theme</p>
            <div className="mt-2 flex gap-2">
              {THEMES.map((t) => (
                <button
                  key={t}
                  type="button"
                  className="rounded-full border border-slate-200 px-3 py-1.5 text-xs font-medium hover:bg-blue-50 hover:border-blue-400 hover:text-blue-600 dark:border-slate-700 dark:hover:bg-blue-950 transition-colors"
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        </Card>

        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">Notifications</h2>
          <div className="mt-2 flex flex-col divide-y divide-slate-100 dark:divide-slate-800">
            <Toggle
              checked={notifications.email}
              onChange={() => setNotifications({ ...notifications, email: !notifications.email })}
              label="Email Notifications"
            />
            <Toggle
              checked={notifications.push}
              onChange={() => setNotifications({ ...notifications, push: !notifications.push })}
              label="Push Notifications"
            />
            <Toggle
              checked={notifications.sms}
              onChange={() => setNotifications({ ...notifications, sms: !notifications.sms })}
              label="SMS Notifications"
            />
          </div>
        </Card>

        <Card className="border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
          <h2 className="text-lg font-semibold">Security</h2>
          <div className="mt-4 flex flex-col gap-4">
            <button
              type="button"
              className="w-fit rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800 transition-colors"
            >
              Change Password
            </button>
            <Toggle
              checked={twoFactor}
              onChange={() => setTwoFactor(!twoFactor)}
              label="Two-Factor Authentication"
            />
          </div>
        </Card>
      </div>

      <Card className="mt-6 border border-slate-200/60 bg-white/70 p-6 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
        <h2 className="text-lg font-semibold">Save Changes</h2>
        <div className="mt-4 flex flex-wrap gap-4">
          <button
            type="button"
            onClick={handleSave}
            className="rounded-lg bg-amber-500 px-6 py-3 font-semibold text-white hover:bg-amber-600 transition-colors"
          >
            {saved ? "Saved ✓" : "Save Changes"}
          </button>
          <button
            type="button"
            className="rounded-lg border border-slate-300 px-6 py-3 font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800 transition-colors"
          >
            Reset
          </button>
        </div>
      </Card>
    </motion.div>
  );
}