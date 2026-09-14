import React from "react";

export const Card: React.FC<{ title: string; subtitle?: string; children: React.ReactNode; className?: string }> = ({
  title,
  subtitle,
  children,
  className,
}) => (
  <div className={`bg-white rounded-2xl border border-slate-200 shadow-sm p-5 ${className || ""}`}>
    <div className="mb-3">
      <h3 className="font-semibold text-slate-800">{title}</h3>
      {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
    </div>
    {children}
  </div>
);

export const Badge: React.FC<{ text: string; color: "gray" | "green" | "amber" | "red" | "blue" }> = ({ text, color }) => {
  const map: Record<string, string> = {
    gray: "bg-slate-100 text-slate-700",
    green: "bg-emerald-100 text-emerald-700",
    amber: "bg-amber-100 text-amber-700",
    red: "bg-red-100 text-red-700",
    blue: "bg-blue-100 text-blue-700",
  };
  return <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${map[color]}`}>{text}</span>;
};

export function severityColor(sev: string): "gray" | "green" | "amber" | "red" | "blue" {
  if (sev === "Critical") return "red";
  if (sev === "High") return "amber";
  if (sev === "Medium") return "blue";
  return "gray";
}

export function statusColor(status: string): "gray" | "green" | "amber" | "red" | "blue" {
  if (status === "Completed") return "green";
  if (status === "In Progress") return "blue";
  if (status === "Blocked" || status === "Delayed") return "red";
  return "gray";
}
