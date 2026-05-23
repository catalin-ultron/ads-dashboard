import { useState } from "react";
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from "recharts";
import {
  DollarSign,
  TrendingUp,
  CheckSquare,
  Target,
  Users,
  Filter,
  ChevronRight,
  BarChart3,
  Boxes,
  Workflow,
} from "lucide-react";

/* ─────────── data ─────────── */

const TIER_DATA = [
  { name: "Tier 1 — Prove", meta: 1400, tiktok: 600, total: 2000, leads: "5-15" },
  { name: "Tier 2 — Validate", meta: 3500, tiktok: 1500, total: 5000, leads: "15-40" },
  { name: "Tier 3 — Scale", meta: 7000, tiktok: 3000, total: 10000, leads: "40-80" },
];

const SPEND_PROJECTION = [
  { day: "W1", meta: 350, tiktok: 150, total: 500 },
  { day: "W2", meta: 350, tiktok: 150, total: 500 },
  { day: "W3", meta: 700, tiktok: 300, total: 1000 },
  { day: "W4", meta: 700, tiktok: 300, total: 1000 },
  { day: "W5", meta: 875, tiktok: 375, total: 1250 },
  { day: "W6", meta: 875, tiktok: 375, total: 1250 },
  { day: "W7", meta: 875, tiktok: 375, total: 1250 },
  { day: "W8", meta: 875, tiktok: 375, total: 1250 },
  { day: "W9", meta: 1750, tiktok: 750, total: 2500 },
  { day: "W10", meta: 1750, tiktok: 750, total: 2500 },
  { day: "W11", meta: 1750, tiktok: 750, total: 2500 },
  { day: "W12", meta: 1750, tiktok: 750, total: 2500 },
];

const FUNNEL_STAGES = [
  { name: "Impressions", meta: 45000, tiktok: 60000, color: "#1877f2" },
  { name: "Reach", meta: 15000, tiktok: 25000, color: "#7c3aed" },
  { name: "Clicks", meta: 1200, tiktok: 1500, color: "#7c3aed" },
  { name: "Landing", meta: 800, tiktok: 900, color: "#7c3aed" },
  { name: "Leads", meta: 25, tiktok: 30, color: "#7c3aed" },
  { name: "MQLs", meta: 12, tiktok: 15, color: "#10b981" },
  { name: "SQLs", meta: 3, tiktok: 4, color: "#10b981" },
];

const CAMPAIGN_WORKFLOW = [
  {
    id: "c1",
    name: "Cold Awareness — Founder POV",
    platform: "Meta",
    status: "active",
    spend: 483,
    budget: 700,
    ctr: "1.2%",
    cpc: "$2.40",
    impressions: 28200,
    leads: 8,
    layer: "TOFU",
  },
  {
    id: "c2",
    name: "Consideration — 90-Day System",
    platform: "Meta",
    status: "active",
    spend: 312,
    budget: 490,
    ctr: "0.9%",
    cpc: "$2.80",
    impressions: 14200,
    leads: 4,
    layer: "MOFU",
  },
  {
    id: "c3",
    name: "Conversion — Free GTM Audit",
    platform: "Meta",
    status: "paused",
    spend: 180,
    budget: 280,
    ctr: "0.6%",
    cpc: "$3.50",
    impressions: 8100,
    leads: 2,
    layer: "BOFU",
  },
  {
    id: "c4",
    name: "Cold — Founder Marketing Team",
    platform: "TikTok",
    status: "active",
    spend: 195,
    budget: 300,
    ctr: "1.4%",
    cpc: "$1.60",
    impressions: 18500,
    leads: 5,
    layer: "TOFU",
  },
  {
    id: "c5",
    name: "Consideration — 3-Step System",
    platform: "TikTok",
    status: "review",
    spend: 95,
    budget: 180,
    ctr: "0.8%",
    cpc: "$2.10",
    impressions: 7200,
    leads: 2,
    layer: "MOFU",
  },
  {
    id: "c6",
    name: "Conversion — Book Call",
    platform: "TikTok",
    status: "draft",
    spend: 0,
    budget: 120,
    ctr: "—",
    cpc: "—",
    impressions: 0,
    leads: 0,
    layer: "BOFU",
  },
];

const KPIDATA = [
  { label: "Blended CPL", target: "<$50", current: "$44", status: "good", delta: "-12%" },
  { label: "Meta CPL", target: "<$60", current: "$58", status: "warning", delta: "+3%" },
  { label: "TikTok CPL", target: "<$40", current: "$36", status: "good", delta: "-8%" },
  { label: "Blended CTR", target: ">1.0%", current: "1.05%", status: "good", delta: "+5%" },
  { label: "MQL Rate", target: ">30%", current: "32%", status: "good", delta: "+2%" },
  { label: "SQL Rate", target: ">10%", current: "9%", status: "warning", delta: "-1%" },
  { label: "Demo Show", target: ">50%", current: "54%", status: "good", delta: "+4%" },
  { label: "Spend Pace", target: "On Track", current: "98%", status: "good", delta: "0%" },
];

const CREATIVE_PIPELINE = [
  { name: "Founder burnout POV (reel)", status: "live", platform: "Meta", spend: "$483", ctr: "1.2%", id: "cr1" },
  { name: "90-day system walkthrough", status: "live", platform: "Meta", spend: "$312", ctr: "0.9%", id: "cr2" },
  { name: "GTM audit lead form", status: "paused", platform: "Meta", spend: "$180", ctr: "0.6%", id: "cr3" },
  { name: "POV: You're the marketing team", status: "live", platform: "TikTok", spend: "$195", ctr: "1.4%", id: "cr4" },
  { name: "3-step breakdown", status: "review", platform: "TikTok", spend: "$95", ctr: "0.8%", id: "cr5" },
  { name: "Founder call CTA", status: "draft", platform: "TikTok", spend: "$0", ctr: "—", id: "cr6" },
  { name: "Behind the scenes: building pipeline", status: "in_prod", platform: "Both", spend: "$0", ctr: "—", id: "cr7" },
  { name: "Customer testimonial: founder story", status: "in_prod", platform: "Meta", spend: "$0", ctr: "—", id: "cr8" },
];

const AUDIENCE_SEGMENTS = [
  { name: "Founder-led SaaS < 50 employees", platform: "Meta", size: "2.4M", overlap: "Low", cpm: "$22", performance: "Best" },
  { name: "Head of Growth / VP Marketing", platform: "Meta", size: "890K", overlap: "Med", cpm: "$28", performance: "Strong" },
  { name: "Early-stage B2B SaaS", platform: "TikTok", size: "1.8M", overlap: "Low", cpm: "$9", performance: "Best" },
  { name: "Startup founder + productivity", platform: "TikTok", size: "3.2M", overlap: "High", cpm: "$8", performance: "Good" },
  { name: "Lookalike — Top 1% converters", platform: "Both", size: "230K", overlap: "—", cpm: "$18", performance: "Testing" },
];

/* ─────────── components ─────────── */

const COLORS = {
  meta: "#1877f2",
  tiktok: "#ff0050",
  accent: "#7c3aed",
  good: "#10b981",
  warning: "#f59e0b",
  danger: "#ef4444",
  textBright: "#f0f2f5",
  textMuted: "#8892b0",
  surface: "#1f2833",
  surfaceLight: "#2a3441",
};

function Card({ children, className = "", style }: { children: React.ReactNode; className?: string; style?: React.CSSProperties }) {
  return (
    <div className={`rounded-xl p-5 border border-white/[0.06] bg-[#1a1d29] shadow-lg ${className}`} style={style}>
      {children}
    </div>
  );
}

function SectionHeader({ icon: Icon, title, action }: { icon: any; title: string; action?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2.5">
        <div className="p-1.5 rounded-md bg-white/5">
          <Icon size={18} className="text-white/80" />
        </div>
        <h2 className="text-base font-semibold text-[#f0f2f5]">{title}</h2>
      </div>
      {action}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    paused: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    review: "bg-violet-500/10 text-violet-400 border-violet-500/20",
    draft: "bg-slate-500/10 text-slate-400 border-slate-500/20",
    live: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    in_prod: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    good: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  };
  const labels: Record<string, string> = {
    active: "Active",
    paused: "Paused",
    review: "Review",
    draft: "Draft",
    live: "Live",
    in_prod: "In Prod",
    good: "On Track",
    warning: "Watch",
  };
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded border ${styles[status] || styles.draft}`}>
      {labels[status] || status}
    </span>
  );
}

function KPICard({ label, current, target, status, delta }: (typeof KPIDATA)[0]) {
  const isGood = status === "good";
  return (
    <Card className="flex flex-col justify-between">
      <div className="flex justify-between items-start mb-3">
        <p className="text-xs text-[#8892b0] uppercase tracking-wide">{label}</p>
        <StatusBadge status={status} />
      </div>
      <div>
        <p className="text-2xl font-bold text-[#f0f2f5] mb-1">{current}</p>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-medium ${isGood ? "text-emerald-400" : "text-amber-400"}`}>
            {delta}
          </span>
          <span className="text-xs text-[#8892b0]">Target: {target}</span>
        </div>
      </div>
    </Card>
  );
}

/* ─────────── main app ─────────── */

export default function App() {
  const [selectedTier, setSelectedTier] = useState(0);
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterPlatform, setFilterPlatform] = useState("all");

  const tier = TIER_DATA[selectedTier];
  const pieData = [
    { name: "Meta (Instagram)", value: tier.meta, color: COLORS.meta },
    { name: "TikTok", value: tier.tiktok, color: COLORS.tiktok },
  ];

  const filteredWorkflow = CAMPAIGN_WORKFLOW.filter((c) => {
    if (filterStatus !== "all" && c.status !== filterStatus) return false;
    if (filterPlatform !== "all" && c.platform !== filterPlatform) return false;
    return true;
  });

  const totalSpend = CAMPAIGN_WORKFLOW.reduce((s, c) => s + c.spend, 0);
  const totalBudget = CAMPAIGN_WORKFLOW.reduce((s, c) => s + c.budget, 0);
  const totalLeads = CAMPAIGN_WORKFLOW.reduce((s, c) => s + c.leads, 0);

  return (
    <div className="min-h-screen bg-[#0f1115] text-[#c5c6c7] pb-12">
      {/* Top Header */}
      <header className="border-b border-white/[0.06] bg-[#13151a] sticky top-0 z-50">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center">
              <BarChart3 size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-[#f0f2f5]">Ads Command Center</h1>
              <p className="text-xs text-[#8892b0]">NXT Enterprises — Meta + TikTok</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="text-xs text-[#8892b0]">Monthly Budget</p>
              <p className="text-sm font-semibold text-[#f0f2f5]">${(totalBudget).toLocaleString()} / {tier.total.toLocaleString()}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-[#8892b0]">Spend Pace</p>
              <p className="text-sm font-semibold text-emerald-400">{Math.round((totalSpend / totalBudget) * 100)}%</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-[#8892b0]">Leads This Month</p>
              <p className="text-sm font-semibold text-violet-400">{totalLeads}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="px-6 pt-6 max-w-[1600px] mx-auto">
        {/* KPI Row */}
        <section className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
            {KPIDATA.map((kpi) => (
              <KPICard key={kpi.label} {...kpi} />
            ))}
          </div>
        </section>

        {/* Top Row: Budget + Funnel + Projection */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 mb-8">
          {/* Budget Allocation */}
          <div className="xl:col-span-4">
            <SectionHeader icon={DollarSign} title="Budget Allocation" />
            <Card className="h-[380px]">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-xs text-[#8892b0]">Selected Tier</p>
                  <p className="text-lg font-bold text-[#f0f2f5]">{tier.name}</p>
                </div>
                <div className="flex gap-1">
                  {TIER_DATA.map((t, i) => (
                    <button
                      key={t.name}
                      onClick={() => setSelectedTier(i)}
                      className={`px-3 py-1 text-xs rounded-md border transition-all ${
                        selectedTier === i
                          ? "bg-violet-600/20 border-violet-500/40 text-violet-300"
                          : "border-white/5 text-[#8892b0] hover:bg-white/5"
                      }`}
                    >
                      T{i + 1}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="p-3 rounded-lg bg-white/[0.03]">
                  <p className="text-xs text-[#8892b0] mb-1">Meta</p>
                  <p className="text-xl font-bold text-[#1877f2]">${tier.meta.toLocaleString()}</p>
                  <p className="text-xs text-[#8892b0]">{Math.round((tier.meta / tier.total) * 100)}%</p>
                </div>
                <div className="p-3 rounded-lg bg-white/[0.03]">
                  <p className="text-xs text-[#8892b0] mb-1">TikTok</p>
                  <p className="text-xl font-bold text-[#ff0050]">${tier.tiktok.toLocaleString()}</p>
                  <p className="text-xs text-[#8892b0]">{Math.round((tier.tiktok / tier.total) * 100)}%</p>
                </div>
              </div>

              <div className="h-[180px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={75}
                      dataKey="value"
                      stroke="none"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: "#1a1d29",
                        border: "1px solid rgba(255,255,255,0.08)",
                        borderRadius: 8,
                        color: "#c5c6c7",
                        fontSize: 12,
                      }}
                      formatter={(value: any) => [`$${Number(value).toLocaleString()}`, ""] as any}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>

          {/* Funnel Visualization */}
          <div className="xl:col-span-4">
            <SectionHeader icon={Filter} title="Conversion Funnel" />
            <Card className="h-[380px]">
              <div className="space-y-3">
                {FUNNEL_STAGES.map((stage) => {
                  const maxVal = Math.max(stage.meta, stage.tiktok);
                  const metaPct = (stage.meta / maxVal) * 100;
                  const tiktokPct = (stage.tiktok / maxVal) * 100;
                  return (
                    <div key={stage.name}>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-[#f0f2f5] font-medium">{stage.name}</span>
                        <span className="text-[#8892b0]">
                          M: {stage.meta.toLocaleString()} / T: {stage.tiktok.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex gap-1.5">
                        <div className="flex-1 h-5 bg-white/[0.04] rounded overflow-hidden">
                          <div
                            className="h-full bg-[#1877f2] rounded flex items-center justify-end pr-1.5"
                            style={{ width: `${metaPct}%` }}
                          >
                            {metaPct > 30 && (
                              <span className="text-[10px] text-white/90 font-medium">{stage.meta.toLocaleString()}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex-1 h-5 bg-white/[0.04] rounded overflow-hidden">
                          <div
                            className="h-full bg-[#ff0050] rounded flex items-center justify-end pr-1.5"
                            style={{ width: `${tiktokPct}%` }}
                          >
                            {tiktokPct > 30 && (
                              <span className="text-[10px] text-white/90 font-medium">{stage.tiktok.toLocaleString()}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-center gap-6 mt-4 pt-3 border-t border-white/[0.06]">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded bg-[#1877f2]" />
                  <span className="text-xs text-[#8892b0]">Meta</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded bg-[#ff0050]" />
                  <span className="text-xs text-[#8892b0]">TikTok</span>
                </div>
              </div>
            </Card>
          </div>

          {/* Spend Projection */}
          <div className="xl:col-span-4">
            <SectionHeader icon={TrendingUp} title="Spend Projection (12 Weeks)" />
            <Card className="h-[380px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={SPEND_PROJECTION}>
                  <defs>
                    <linearGradient id="metaGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#1877f2" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#1877f2" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="tiktokGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ff0050" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#ff0050" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="day" stroke="#8892b0" fontSize={11} />
                  <YAxis stroke="#8892b0" fontSize={11} tickFormatter={(v) => `$${v}`} />
                  <Tooltip
                    contentStyle={{
                      background: "#1a1d29",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 8,
                      color: "#c5c6c7",
                      fontSize: 12,
                    }}
                  />
                  <Area type="monotone" dataKey="meta" name="Meta" stroke="#1877f2" fill="url(#metaGrad)" strokeWidth={2} />
                  <Area type="monotone" dataKey="tiktok" name="TikTok" stroke="#ff0050" fill="url(#tiktokGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </div>

        {/* Campaign Workflow Board */}
        <section className="mb-8">
          <SectionHeader
            icon={Workflow}
            title={`Campaign Workflow (${filteredWorkflow.length})`}
            action={
              <div className="flex gap-2">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="bg-[#1a1d29] border border-white/[0.08] text-xs rounded-md px-2 py-1 text-[#8892b0] outline-none focus:border-violet-500/40"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="paused">Paused</option>
                  <option value="review">Review</option>
                  <option value="draft">Draft</option>
                </select>
                <select
                  value={filterPlatform}
                  onChange={(e) => setFilterPlatform(e.target.value)}
                  className="bg-[#1a1d29] border border-white/[0.08] text-xs rounded-md px-2 py-1 text-[#8892b0] outline-none focus:border-violet-500/40"
                >
                  <option value="all">All Platforms</option>
                  <option value="Meta">Meta</option>
                  <option value="TikTok">TikTok</option>
                </select>
              </div>
            }
          />
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06] text-[#8892b0] text-xs uppercase tracking-wide">
                    <th className="text-left pb-3 pr-4">Campaign</th>
                    <th className="text-left pb-3 pr-4">Status</th>
                    <th className="text-left pb-3 pr-4">Layer</th>
                    <th className="text-right pb-3 pr-4">Spend</th>
                    <th className="text-right pb-3 pr-4">Budget</th>
                    <th className="text-right pb-3 pr-4">Pace</th>
                    <th className="text-right pb-3 pr-4">CTR</th>
                    <th className="text-right pb-3 pr-4">CPC</th>
                    <th className="text-right pb-3 pr-4">Leads</th>
                    <th className="text-right pb-3">ROI Est.</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredWorkflow.map((c) => {
                    const pace = Math.round((c.spend / c.budget) * 100);
                    const leadValue = c.leads > 0 ? Math.round(c.spend / c.leads) : 0;
                    return (
                      <tr key={c.id} className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                        <td className="py-3 pr-4">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-1.5 h-1.5 rounded-full shrink-0"
                              style={{ background: c.platform === "Meta" ? COLORS.meta : COLORS.tiktok }}
                            />
                            <div>
                              <p className="text-[#f0f2f5] font-medium">{c.name}</p>
                              <p className="text-xs text-[#8892b0]">{c.platform}</p>
                            </div>
                          </div>
                        </td>
                        <td className="py-3 pr-4">
                          <StatusBadge status={c.status} />
                        </td>
                        <td className="py-3 pr-4">
                          <span className="text-xs font-medium px-2 py-0.5 rounded bg-white/[0.05] text-[#8892b0] border border-white/[0.06]">
                            {c.layer}
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-right text-[#f0f2f5]">${c.spend}</td>
                        <td className="py-3 pr-4 text-right text-[#8892b0]">${c.budget}</td>
                        <td className="py-3 pr-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <div className="w-16 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full"
                                style={{
                                  width: `${pace}%`,
                                  background: pace > 90 ? "#ef4444" : pace > 70 ? "#f59e0b" : "#10b981",
                                }}
                              />
                            </div>
                            <span className="text-xs text-[#8892b0]">{pace}%</span>
                          </div>
                        </td>
                        <td className="py-3 pr-4 text-right text-[#f0f2f5]">{c.ctr}</td>
                        <td className="py-3 pr-4 text-right text-[#f0f2f5]">{c.cpc}</td>
                        <td className="py-3 pr-4 text-right text-[#f0f2f5] font-medium">{c.leads}</td>
                        <td className="py-3 text-right text-[#8892b0]">
                          {leadValue > 0 ? `$${leadValue}` : "—"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </section>

        {/* Creative Pipeline + Audience Segments */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
          {/* Creative Pipeline */}
          <div>
            <SectionHeader icon={Boxes} title="Creative Pipeline" />
            <div className="space-y-2">
              {CREATIVE_PIPELINE.map((cr) => (
                <Card key={cr.id} className="p-3 !py-2.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-1 h-8 rounded-full"
                        style={{
                          background:
                            cr.platform === "Meta"
                              ? COLORS.meta
                              : cr.platform === "TikTok"
                              ? COLORS.tiktok
                              : COLORS.accent,
                        }}
                      />
                      <div>
                        <p className="text-sm font-medium text-[#f0f2f5]">{cr.name}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <StatusBadge status={cr.status} />
                          <span className="text-xs text-[#8892b0]">{cr.platform}</span>
                          {cr.spend !== "$0" && (
                            <span className="text-xs text-[#8892b0]">{cr.spend} · {cr.ctr} CTR</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <ChevronRight size={14} className="text-[#8892b0]" />
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* Audience Segments */}
          <div>
            <SectionHeader icon={Users} title="Audience Segments" />
            <Card className="h-full">
              <div className="space-y-3">
                {AUDIENCE_SEGMENTS.map((seg) => (
                  <div
                    key={seg.name}
                    className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.04] hover:border-white/[0.08] transition-colors"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="text-sm font-medium text-[#f0f2f5]">{seg.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span
                            className="text-xs px-1.5 py-0.5 rounded"
                            style={{
                              background:
                                seg.platform === "Meta"
                                  ? "rgba(24,119,242,0.12)"
                                  : seg.platform === "TikTok"
                                  ? "rgba(255,0,80,0.12)"
                                  : "rgba(124,58,237,0.12)",
                              color:
                                seg.platform === "Meta"
                                  ? "#1877f2"
                                  : seg.platform === "TikTok"
                                  ? "#ff0050"
                                  : "#a78bfa",
                            }}
                          >
                            {seg.platform}
                          </span>
                          <span className="text-xs text-[#8892b0]">{seg.size} reach</span>
                        </div>
                      </div>
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded border ${
                          seg.performance === "Best"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : seg.performance === "Strong"
                            ? "bg-blue-500/10 text-blue-400 border-blue-500/20"
                            : seg.performance === "Good"
                            ? "bg-violet-500/10 text-violet-400 border-violet-500/20"
                            : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                        }`}
                      >
                        {seg.performance}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-[#8892b0]">
                      <span>Overlap: {seg.overlap}</span>
                      <span>CPM: {seg.cpm}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>

        {/* Pre-Launch Checklist */}
        <section className="mb-8">
          <SectionHeader icon={CheckSquare} title="Pre-Launch Checklist" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              "Creative assets produced for all 8 launch ads",
              "Exclusion audiences built (CRM list, employees)",
              "Conversion events tested in Events Manager",
              "UTM taxonomy documented and shared with sales",
              "Landing pages load <2s on mobile",
              "Lead form routing tested end-to-end",
              "Budget caps set per layer in Ads Manager",
              "Daily monitoring schedule defined",
              "Kill rules: pause ads with CTR <0.3% (Meta) / <0.2% (TikTok)",
            ].map((item, idx) => (
              <Card key={idx} className="!p-3">
                <label className="flex items-start gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    className="mt-0.5 w-4 h-4 rounded border-white/20 bg-[#1a1d29] text-violet-500 focus:ring-violet-500/40"
                  />
                  <span className="text-sm text-[#8892b0] group-hover:text-[#c5c6c7] transition-colors leading-relaxed">
                    {item}
                  </span>
                </label>
              </Card>
            ))}
          </div>
        </section>

        {/* 90-Day Roadmap */}
        <section className="mb-10">
          <SectionHeader icon={Target} title="90-Day Campaign Roadmap" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              {
                stage: "Days 1-14",
                title: "Launch & Learn",
                items: ["Launch all 8 ads", "Lowest Cost bidding", "Daily monitoring", "Validate creative-market fit"],
                color: "#1877f2",
              },
              {
                stage: "Days 15-30",
                title: "Optimize & Rotate",
                items: ["Double top performers", "New creative variants", "Build retargeting pools", "Layer 1 engagement focus"],
                color: "#7c3aed",
              },
              {
                stage: "Days 31-60",
                title: "Validate & Ramp",
                items: ["Test Cost Cap bidding", "Tier 2 readiness", "Refine exclusions", "Add Lookalike audiences"],
                color: "#ff0050",
              },
              {
                stage: "Days 61-90",
                title: "Scale or Pivot",
                items: ["Move to Tier 3 ($10K)", "Batch production", "Review blended CAC", "Channel mix decision"],
                color: "#10b981",
              },
            ].map((phase) => (
              <Card key={phase.stage} className="border-t-2" style={{ borderTopColor: phase.color }}>
                <p className="text-xs text-[#8892b0] mb-1">{phase.stage}</p>
                <h3 className="text-sm font-semibold text-[#f0f2f5] mb-3">{phase.title}</h3>
                <ul className="space-y-2">
                  {phase.items.map((item) => (
                    <li key={item} className="text-xs text-[#8892b0] flex items-start gap-2">
                      <ChevronRight size={12} className="mt-0.5 shrink-0 text-[#8892b0]" />
                      {item}
                    </li>
                  ))}
                </ul>
              </Card>
            ))}
          </div>
        </section>

        {/* Footer */}
        <footer className="text-center text-xs text-[#8892b0] border-t border-white/[0.06] pt-6">
          NXT Enterprises — Pre-seed B2B SaaS. Keep it systems-minded. Cut what doesn't move pipeline by Day 21.
        </footer>
      </main>
    </div>
  );
}
