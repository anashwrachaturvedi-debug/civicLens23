export function formatDate(date) {
  const d = date instanceof Date ? date : new Date(date);
  return d.toLocaleDateString("en-IN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function formatTime(date) {
  const d = date instanceof Date ? date : new Date(date);
  return d.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function capitalize(text = "") {
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

export function truncateText(text = "", maxLength = 80) {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength).trim()}...`;
}

export function generateIssueId() {
  const random = Math.floor(1000 + Math.random() * 9000);
  return `CL-${random}`;
}

export function getPriorityColor(priority) {
  const map = {
    Critical: "red",
    High: "orange",
    Medium: "amber",
    Low: "slate",
  };
  return map[priority] || "slate";
}

export function getStatusColor(status) {
  const map = {
    Pending: "slate",
    Assigned: "blue",
    "In Progress": "amber",
    Resolved: "green",
  };
  return map[status] || "slate";
}

export function getSeverityColor(score) {
  if (score >= 80) return "red";
  if (score >= 60) return "orange";
  if (score >= 40) return "amber";
  return "slate";
}

export function getInitials(name = "") {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");
}

export function debounce(fn, delay = 300) {
  let timeoutId;
  return function debounced(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}