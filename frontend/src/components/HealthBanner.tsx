import React from "react";
import type { ProjectHealth } from "../types";

const styles: Record<ProjectHealth, { bg: string; text: string; dot: string }> = {
  "On Track": { bg: "bg-emerald-50 border-emerald-200", text: "text-emerald-800", dot: "bg-emerald-500" },
  "At Risk": { bg: "bg-amber-50 border-amber-200", text: "text-amber-800", dot: "bg-amber-500" },
  "Delayed": { bg: "bg-red-50 border-red-200", text: "text-red-800", dot: "bg-red-500" },
};

const HealthBanner: React.FC<{ health: ProjectHealth; explanation: string; usedLlm: boolean }> = ({
  health,
  explanation,
  usedLlm,
}) => {
  const s = styles[health];
  return (
    <div className={`rounded-2xl border ${s.bg} p-5 flex items-start justify-between gap-4`}>
      <div className="flex items-start gap-3">
        <span className={`mt-1 h-3 w-3 rounded-full ${s.dot} shrink-0`} />
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500 font-semibold">Project Health</p>
          <p className={`text-xl font-bold ${s.text}`}>{health}</p>
          <p className="text-sm text-slate-600 mt-1 max-w-2xl">{explanation}</p>
        </div>
      </div>
      <span className="text-xs px-2 py-1 rounded-full bg-white border border-slate-200 text-slate-500 whitespace-nowrap">
        {usedLlm ? "Gemini-enhanced narrative" : "Rule-engine narrative"}
      </span>
    </div>
  );
};

export default HealthBanner;
