import { Routes, Route } from "react-router-dom";

import AuthorityLayout from "./layouts/AuthorityLayout";
import CitizenLayout from "./layouts/CitizenLayout";

import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import ReportIssue from "./pages/ReportIssue";
import Success from "./pages/Success";
import MapView from "./pages/MapView";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route element={<CitizenLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/report" element={<ReportIssue />} />
        <Route path="/success" element={<Success />} />
        <Route path="/map" element={<MapView />} />
      </Route>

      <Route element={<AuthorityLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}