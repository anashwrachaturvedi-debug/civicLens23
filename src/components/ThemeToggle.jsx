import { useState, useEffect } from "react";
import { FaSun, FaMoon } from "react-icons/fa";

const ThemeToggle = () => {
  const getInitialTheme = () => {
    if (typeof window === "undefined") return "light";

    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) return savedTheme;

    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  };

  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    document.documentElement.classList.add("transition-colors", "duration-300");

    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }

    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleChange = (e) => {
      if (!localStorage.getItem("theme")) {
        setTheme(e.matches ? "dark" : "light");
      }
    };

    mediaQuery.addEventListener("change", handleChange);

    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  const toggleTheme = () =>
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${
        theme === "dark" ? "light" : "dark"
      } mode`}
      title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
      className="group relative flex h-11 w-11 items-center justify-center rounded-full border border-white/20 bg-white/10 text-slate-700 shadow-lg backdrop-blur-md transition-all duration-300 hover:scale-105 hover:border-blue-400 hover:bg-blue-500/10 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-slate-700 dark:bg-slate-800/60 dark:text-yellow-300 dark:hover:border-blue-400 dark:hover:bg-blue-500/10 dark:hover:text-yellow-200 dark:focus:ring-offset-slate-900"
    >
      <span
        className={`absolute transition-all duration-300 ${
          theme === "dark"
            ? "scale-100 rotate-0 opacity-100"
            : "scale-0 -rotate-90 opacity-0"
        }`}
      >
        <FaMoon className="text-lg" />
      </span>

      <span
        className={`absolute transition-all duration-300 ${
          theme === "light"
            ? "scale-100 rotate-0 opacity-100"
            : "scale-0 rotate-90 opacity-0"
        }`}
      >
        <FaSun className="text-lg" />
      </span>
    </button>
  );
};

export default ThemeToggle;