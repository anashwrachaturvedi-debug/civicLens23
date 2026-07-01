export const dashboardStats = {
  totalIssues: 1284,
  resolvedIssues: 962,
  pendingIssues: 285,
  criticalIssues: 37,
  aiAccuracy: 94.6,
  resolutionRate: 75,
  avgResponseTime: "6.2 hrs",
  citiesMonitored: 12,
};

export const monthlyReports = [
  { month: "Jan", reports: 180, resolved: 130 },
  { month: "Feb", reports: 210, resolved: 165 },
  { month: "Mar", reports: 195, resolved: 150 },
  { month: "Apr", reports: 240, resolved: 198 },
  { month: "May", reports: 225, resolved: 184 },
  { month: "Jun", reports: 268, resolved: 221 },
  { month: "Jul", reports: 252, resolved: 209 },
  { month: "Aug", reports: 231, resolved: 190 },
  { month: "Sep", reports: 244, resolved: 205 },
  { month: "Oct", reports: 260, resolved: 222 },
  { month: "Nov", reports: 238, resolved: 196 },
  { month: "Dec", reports: 219, resolved: 178 },
];

export const issueCategories = [
  { label: "Potholes", value: 38, tone: "red" },
  { label: "Garbage", value: 27, tone: "amber" },
  { label: "Waterlogging", value: 19, tone: "blue" },
  { label: "Streetlights", value: 9, tone: "slate" },
  { label: "Road Damage", value: 5, tone: "orange" },
  { label: "Drainage Issues", value: 2, tone: "green" },
];

export const priorityDistribution = [
  { label: "Critical", value: 37, tone: "red" },
  { label: "High", value: 214, tone: "orange" },
  { label: "Medium", value: 498, tone: "amber" },
  { label: "Low", value: 535, tone: "slate" },
];

export const statusDistribution = [
  { label: "Pending", value: 285, tone: "slate" },
  { label: "Assigned", value: 196, tone: "blue" },
  { label: "In Progress", value: 158, tone: "amber" },
  { label: "Resolved", value: 962, tone: "green" },
];