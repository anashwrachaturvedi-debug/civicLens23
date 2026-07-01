import { useState } from "react";
import { HiOutlineLocationMarker, HiOutlineExclamationCircle } from "react-icons/hi";

export default function LocationPicker({ location, setLocation }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleDetectLocation() {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.");
      return;
    }

    setLoading(true);
    setError("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude.toFixed(6),
          longitude: position.coords.longitude.toFixed(6),
        });
        setLoading(false);
      },
      (geoError) => {
        setError(geoError.message || "Unable to detect your location.");
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  function handleChange(field, value) {
    setLocation({ ...location, [field]: value });
  }

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/50">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <span className="flex items-center gap-2 text-sm font-medium">
          <HiOutlineLocationMarker className="text-blue-500" />
          Location
        </span>
        <button
          type="button"
          onClick={handleDetectLocation}
          disabled={loading}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 disabled:opacity-60 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          {loading ? "Detecting..." : "Use Current Location"}
        </button>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm">
          Latitude
          <input
            type="text"
            readOnly
            value={location?.latitude || ""}
            placeholder="Not set"
            className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-300"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Longitude
          <input
            type="text"
            readOnly
            value={location?.longitude || ""}
            placeholder="Not set"
            className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-300"
          />
        </label>
      </div>

      {!location?.latitude && (
        <div className="flex gap-2">
          <input
            type="number"
            step="any"
            placeholder="Enter latitude manually"
            onChange={(event) => handleChange("latitude", event.target.value)}
            className="w-1/2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
          />
          <input
            type="number"
            step="any"
            placeholder="Enter longitude manually"
            onChange={(event) => handleChange("longitude", event.target.value)}
            className="w-1/2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-800 dark:bg-slate-900"
          />
        </div>
      )}

      {error && (
        <p className="flex items-center gap-2 text-sm text-red-500" role="alert">
          <HiOutlineExclamationCircle /> {error}
        </p>
      )}
    </div>
  );
}