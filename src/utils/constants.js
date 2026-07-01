export const APP_NAME = "CivicLens AI";
export const TAGLINE = "Fixing Cities Before Citizens Complain.";

export const NAV_LINKS = [
  { label: "Product", path: "/" },
  { label: "How It Works", path: "/#how-it-works" },
  { label: "Dashboard", path: "/dashboard" },
  { label: "Contact", path: "/#contact" },
];

export const DASHBOARD_STATS = [
  { label: "Total Issues", key: "totalIssues" },
  { label: "Critical Issues", key: "criticalIssues" },
  { label: "Resolved Issues", key: "resolvedIssues" },
  { label: "AI Detection Accuracy", key: "aiAccuracy" },
];

export const ISSUE_CATEGORIES = [
  "Pothole",
  "Garbage Accumulation",
  "Waterlogging",
  "Damaged Road",
  "Broken Streetlight",
];

export const ISSUE_PRIORITIES = ["Critical", "High", "Medium", "Low"];

export const ISSUE_STATUSES = ["Pending", "Assigned", "In Progress", "Resolved"];

export const SEVERITY_LEVELS = [
  { label: "Critical", min: 80, max: 100, tone: "red" },
  { label: "High", min: 60, max: 79, tone: "orange" },
  { label: "Medium", min: 40, max: 59, tone: "amber" },
  { label: "Low", min: 0, max: 39, tone: "slate" },
];

export const THEME_OPTIONS = ["Light", "Dark", "System"];

export const CONTACT_INFO = {
  email: "support@civiclens.ai",
  phone: "+91 98765 43210",
  address: "Civic Tech Innovation Hub, Sector 21, Kanpur, UP, India",
};

export const SOCIAL_LINKS = [
  { label: "Twitter", url: "https://twitter.com/civiclensai" },
  { label: "LinkedIn", url: "https://linkedin.com/company/civiclensai" },
  { label: "GitHub", url: "https://github.com/civiclensai" },
];