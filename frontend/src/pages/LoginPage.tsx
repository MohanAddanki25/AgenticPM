import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getApiErrorMessage } from "../utils/errors";

/* ------------------------------------------------------------------ */
/*  Design tokens                                                      */
/*  ink      #0B1626  deep navy, control-room background               */
/*  panel    #12233A  raised surfaces on the dark side                 */
/*  cobalt   #2454FF  primary action                                   */
/*  signal   red #FF6B6B / amber #FFB84D / green #4ADE9A  risk levels  */
/*  paper    #F4F6FA  form side background                             */
/*  Fonts: Bricolage Grotesque (headlines), Instrument Sans (UI text)  */
/* ------------------------------------------------------------------ */

type Severity = "high" | "medium" | "low" | "info";

interface AgentEvent {
  agent: string;
  project: string;
  message: string;
  severity: Severity;
}

const EVENT_POOL: AgentEvent[] = [
  {
    agent: "Schedule agent",
    project: "Apollo ERP Migration",
    message: "3 tasks are trending 4 days late.",
    severity: "high",
  },
  {
    agent: "Budget agent",
    project: "Mobile Banking Revamp",
    message: "Spend is 12% ahead of plan.",
    severity: "medium",
  },
  {
    agent: "Dependency agent",
    project: "Data Lake Rollout",
    message: "Vendor API access confirmed.",
    severity: "low",
  },
  {
    agent: "Resource agent",
    project: "Apollo ERP Migration",
    message: "2 engineers are allocated above 110%.",
    severity: "high",
  },
  {
    agent: "Risk agent",
    project: "Portfolio",
    message: "Mitigation plan drafted for the Apollo delay.",
    severity: "info",
  },
];

const PROJECTS = [
  { name: "Apollo ERP Migration", phase: "Build", score: 72, level: "High" },
  { name: "Mobile Banking Revamp", phase: "Testing", score: 41, level: "Medium" },
  { name: "Data Lake Rollout", phase: "Planning", score: 18, level: "Low" },
];

const SEVERITY_STYLES: Record<Severity, { dot: string; text: string; bar: string }> = {
  high: { dot: "bg-[#FF6B6B]", text: "text-[#FF9A9A]", bar: "bg-[#FF6B6B]" },
  medium: { dot: "bg-[#FFB84D]", text: "text-[#FFCE85]", bar: "bg-[#FFB84D]" },
  low: { dot: "bg-[#4ADE9A]", text: "text-[#86EDBB]", bar: "bg-[#4ADE9A]" },
  info: { dot: "bg-[#7FA2FF]", text: "text-[#A9C0FF]", bar: "bg-[#7FA2FF]" },
};

const LEVEL_TO_SEVERITY: Record<string, Severity> = {
  High: "high",
  Medium: "medium",
  Low: "low",
};

/* ------------------------------ Icons ------------------------------ */

const LogoMark: React.FC<{ className?: string }> = ({ className }) => (
  <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
    <rect width="32" height="32" rx="9" fill="#2454FF" />
    <circle cx="16" cy="16" r="9" fill="none" stroke="#fff" strokeOpacity=".35" strokeWidth="1.5" />
    <circle cx="16" cy="16" r="4.5" fill="none" stroke="#fff" strokeOpacity=".6" strokeWidth="1.5" />
    <path d="M16 16 L23.5 9.5" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
    <circle cx="23.5" cy="9.5" r="2.2" fill="#FFB84D" />
  </svg>
);

const EyeIcon: React.FC<{ off?: boolean }> = ({ off }) => (
  <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" />
    <circle cx="12" cy="12" r="3" />
    {off && <path d="M4 4l16 16" />}
  </svg>
);

const AlertIcon: React.FC = () => (
  <svg viewBox="0 0 24 24" className="mt-0.5 h-4 w-4 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7.5v5M12 16.2v.1" />
  </svg>
);

const Spinner: React.FC = () => (
  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity=".3" strokeWidth="3" />
    <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
  </svg>
);

/* ------------------------- Live agent feed ------------------------- */

const AgentFeed: React.FC = () => {
  const [items, setItems] = useState<(AgentEvent & { id: number })[]>(
    EVENT_POOL.slice(0, 3)
      .map((ev, i) => ({ ...ev, id: i }))
      .reverse()
  );

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;
    let counter = 3;
    const timer = window.setInterval(() => {
      const ev = EVENT_POOL[counter % EVENT_POOL.length];
      const id = counter;
      counter += 1;
      setItems((prev) => [{ ...ev, id }, ...prev].slice(0, 3));
    }, 3600);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div>
      <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-300">
        <span className="relative flex h-2 w-2">
          <span className="pulse-ring absolute inline-flex h-full w-full rounded-full bg-[#4ADE9A]" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-[#4ADE9A]" />
        </span>
        Agents are monitoring 3 projects
      </div>
      <ul className="space-y-2" aria-live="off">
        {items.map((it) => {
          const s = SEVERITY_STYLES[it.severity];
          return (
            <li
              key={it.id}
              className="feed-in flex gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3"
            >
              <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${s.dot}`} />
              <div className="min-w-0">
                <p className="text-sm text-slate-100">
                  <span className={`font-medium ${s.text}`}>{it.agent}</span>
                  <span className="text-slate-400"> on {it.project}</span>
                </p>
                <p className="text-sm text-slate-300">{it.message}</p>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

/* --------------------------- Risk board ---------------------------- */

const RiskBoard: React.FC = () => (
  <div className="rounded-2xl border border-white/10 bg-[#12233A] p-5">
    <div className="mb-4 flex items-baseline justify-between">
      <h2 className="font-display text-base font-semibold text-white">Project risk today</h2>
      <span className="text-xs text-slate-400">Score out of 100</span>
    </div>
    <ul className="space-y-4">
      {PROJECTS.map((p) => {
        const s = SEVERITY_STYLES[LEVEL_TO_SEVERITY[p.level]];
        return (
          <li key={p.name}>
            <div className="mb-1.5 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-slate-100">{p.name}</p>
                <p className="text-xs text-slate-400">{p.phase} phase</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-medium ${s.text}`}>{p.level}</span>
                <span className="w-8 text-right font-display text-lg font-semibold tabular-nums text-white">
                  {p.score}
                </span>
              </div>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
              <div
                className={`bar-grow h-full rounded-full ${s.bar}`}
                style={{ width: `${p.score}%` }}
              />
            </div>
          </li>
        );
      })}
    </ul>
  </div>
);

/* ------------------------------ Page ------------------------------- */

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("pm@example.com");
  const [password, setPassword] = useState("password123");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err: any) {
      setError(getApiErrorMessage(err, "Login failed"));
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "h-11 w-full rounded-lg border border-slate-300 bg-white px-3.5 text-[15px] text-slate-900 placeholder:text-slate-400 " +
    "transition-colors hover:border-slate-400 focus:border-[#2454FF] focus:outline-none focus:ring-4 focus:ring-[#2454FF]/15";

  return (
    <div className="login-root flex min-h-screen flex-col bg-[#F4F6FA] lg:flex-row">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700&family=Instrument+Sans:wght@400;500;600&display=swap');
        .login-root { font-family: 'Instrument Sans', system-ui, -apple-system, 'Segoe UI', sans-serif; }
        .login-root .font-display { font-family: 'Bricolage Grotesque', 'Instrument Sans', system-ui, sans-serif; }
        @keyframes feedIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: none; } }
        @keyframes barGrow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
        @keyframes pulseRing { 0% { transform: scale(1); opacity: .6; } 80%, 100% { transform: scale(2.6); opacity: 0; } }
        .login-root .feed-in { animation: feedIn .45s ease-out; }
        .login-root .bar-grow { transform-origin: left; animation: barGrow .9s cubic-bezier(.2,.7,.2,1) both; }
        .login-root .pulse-ring { animation: pulseRing 2s ease-out infinite; }
        @media (prefers-reduced-motion: reduce) {
          .login-root .feed-in, .login-root .bar-grow, .login-root .pulse-ring { animation: none; }
        }
      `}</style>

      {/* Brand side */}
      <section className="relative flex flex-col justify-between bg-[#0B1626] px-6 py-8 text-white sm:px-10 lg:w-[54%] lg:px-14 lg:py-12">
        <div className="flex items-center gap-3">
          <LogoMark className="h-9 w-9" />
          <span className="text-sm font-medium text-slate-300">Project risk workspace</span>
        </div>

        <div className="my-8 max-w-xl lg:my-0">
          <h1 className="font-display text-[1.75rem] font-semibold leading-[1.12] tracking-tight text-balance sm:text-4xl xl:text-[3.25rem]">
            Agentic AI Project Management &amp; Risk Monitoring System
          </h1>
          <p className="mt-4 max-w-md text-[15px] leading-relaxed text-slate-300 lg:mt-5 lg:text-base">
            AI agents watch your schedules, budgets, and team load, then flag risk before it turns into delay.
          </p>
        </div>

        <div className="hidden space-y-6 lg:block">
          <RiskBoard />
          <AgentFeed />
        </div>
      </section>

      {/* Form side */}
      <main className="flex flex-1 items-center justify-center px-5 py-10 sm:px-8">
        <div className="w-full max-w-[420px]">
          <div className="rounded-2xl border border-slate-200 bg-white p-7 shadow-[0_1px_2px_rgba(15,23,42,0.05),0_12px_32px_-12px_rgba(15,23,42,0.12)] sm:p-9">
            <h2 className="font-display text-[1.65rem] font-semibold tracking-tight text-slate-900">Sign in</h2>
            <p className="mt-1.5 text-[15px] text-slate-500">Open your project risk dashboard.</p>

            <form onSubmit={handleSubmit} className="mt-7 space-y-5" noValidate={false}>
              <div>
                <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-700">
                  Work email
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={inputClass}
                />
              </div>

              <div>
                <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-700">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    required
                    autoComplete="current-password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={`${inputClass} pr-11`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    aria-pressed={showPassword}
                    className="absolute inset-y-0 right-0 flex w-11 items-center justify-center rounded-r-lg text-slate-400 transition-colors hover:text-slate-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[#2454FF]/15"
                  >
                    <EyeIcon off={showPassword} />
                  </button>
                </div>
              </div>

              {error && (
                <div
                  role="alert"
                  className="flex gap-2 rounded-lg border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm text-red-700"
                >
                  <AlertIcon />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-[#2454FF] text-[15px] font-semibold text-white shadow-[0_1px_0_rgba(255,255,255,0.15)_inset,0_6px_16px_-6px_rgba(36,84,255,0.7)] transition hover:bg-[#1B44DB] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[#2454FF]/30 active:translate-y-px disabled:cursor-not-allowed disabled:opacity-70"
              >
                {loading && <Spinner />}
                {loading ? "Signing in…" : "Sign in"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-slate-500">
              New to the platform?{" "}
              <Link
                to="/register"
                className="font-semibold text-[#2454FF] underline-offset-4 hover:underline focus-visible:rounded focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[#2454FF]/20"
              >
                Create an account
              </Link>
            </p>
          </div>

          <div className="mt-4 rounded-xl border border-dashed border-slate-300 px-4 py-3 text-[13px] leading-relaxed text-slate-500">
            <span className="font-medium text-slate-700">Demo account.</span> Run{" "}
            <code className="rounded bg-slate-200/70 px-1.5 py-0.5 text-[12px] text-slate-800">python seed_demo.py</code>{" "}
            in the backend to create <span className="text-slate-700">pm@example.com</span> /{" "}
            <span className="text-slate-700">password123</span> with sample project data.
          </div>
        </div>
      </main>
    </div>
  );
};

export default LoginPage;
