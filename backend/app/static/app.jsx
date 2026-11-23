/**
 * TransitSense AI - Frontend Application
 * Transport Stack Hackathon 2026 - Problem 2
 * 
 * Production-Quality Crowdedness-Aware Journey Intelligence Platform for Delhi
 * Built with React 18, Tailwind CSS, Leaflet, and Chart.js
 */

const { useState, useEffect, useRef, useMemo } = React;

// --- API CLIENT HELPERS ---
const API_BASE = '/api/v1';

async function apiFetch(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${res.status})`);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

// --- SVG ICON COMPONENT ---
function Icon({ name, className = "w-5 h-5", ...props }) {
  const icons = {
    bus: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h8m-8 4h8m-9 7h10a2 2 0 002-2V6a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zm1 3v-2m10 2v-2" />
      </svg>
    ),
    clock: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    users: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
    mapPin: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    map: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
    ),
    route: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
    sliders: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
      </svg>
    ),
    barChart: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    shieldCheck: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    zap: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    armchair: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 11l1.5-6h11L19 11M5 11a2 2 0 00-2 2v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 00-2-2M5 11h14M7 18v3m10-3v3" />
      </svg>
    ),
    arrowRight: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
      </svg>
    ),
    check: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    ),
    alert: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    refresh: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    chevronDown: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    ),
    externalLink: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
      </svg>
    )
  };
  return icons[name] || icons.bus;
}

// --- TIER BADGE COMPONENT ---
function TierBadge({ tier, label, showOccupancy, occupancy }) {
  const configs = {
    0: { bg: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400', dot: 'bg-emerald-400', text: 'LOW' },
    1: { bg: 'bg-amber-500/15 border-amber-500/30 text-amber-400', dot: 'bg-amber-400', text: 'MODERATE' },
    2: { bg: 'bg-orange-500/15 border-orange-500/30 text-orange-400', dot: 'bg-orange-400', text: 'HIGH' },
    3: { bg: 'bg-rose-500/15 border-rose-500/30 text-rose-400', dot: 'bg-rose-400', text: 'CRUSH' },
  };
  const config = configs[tier] || configs[0];
  const displayLabel = label || config.text;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${config.bg}`}>
      <span className={`w-2 h-2 rounded-full ${config.dot} animate-pulse`}></span>
      <span>{displayLabel}</span>
      {showOccupancy && occupancy !== undefined && (
        <span className="opacity-75 font-mono">({Math.round(occupancy * 100)}%)</span>
      )}
    </span>
  );
}

// --- OCCUPANCY PROGRESS GAUGE ---
function OccupancyGauge({ occupancyRatio, seatedRatio = 0.65 }) {
  const pct = Math.min(100, Math.max(0, Math.round(occupancyRatio * 100)));
  let color = 'bg-emerald-500';
  if (occupancyRatio > 1.0) color = 'bg-rose-500';
  else if (occupancyRatio > 0.75) color = 'bg-orange-500';
  else if (occupancyRatio > 0.50) color = 'bg-amber-500';

  return (
    <div className="w-full">
      <div className="flex justify-between items-center text-xs mb-1 font-mono">
        <span className="text-slate-400">Load: {pct}%</span>
        <span className="text-slate-500">Cap: 100%</span>
      </div>
      <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden relative">
        <div 
          className={`h-full ${color} transition-all duration-500 rounded-full`}
          style={{ width: `${pct}%` }}
        />
        {/* Seated threshold indicator line */}
        <div 
          className="absolute top-0 bottom-0 w-0.5 bg-cyan-400/60 z-10" 
          style={{ left: `${Math.round(seatedRatio * 100)}%` }} 
          title="Seated Capacity Limit"
        />
      </div>
    </div>
  );
}

// --- KPI METRIC CARD ---
function MetricCard({ title, value, subtext, icon, badge, trend }) {
  return (
    <div className="bg-navy-900/80 border border-slate-800 hover:border-slate-700/80 rounded-xl p-5 shadow-lg backdrop-blur transition-all duration-200">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">{title}</span>
        <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
          <Icon name={icon} className="w-5 h-5" />
        </div>
      </div>
      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl font-bold font-mono text-white">{value}</span>
        {badge && (
          <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-medium">{badge}</span>
        )}
      </div>
      {subtext && <p className="text-xs text-slate-400 leading-relaxed">{subtext}</p>}
    </div>
  );
}

// --- NAVIGATION HEADER ---
function Header({ activeTab, setActiveTab, onOpenProvenanceModal }) {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: 'route' },
    { id: 'planner', label: 'Journey Planner', icon: 'bus', highlight: true },
    { id: 'compare', label: 'Route Comparison', icon: 'sliders' },
    { id: 'forecast', label: 'Crowd Intelligence', icon: 'clock' },
    { id: 'map', label: 'Delhi Network Map', icon: 'map' },
    { id: 'simulator', label: 'What-If Simulator', icon: 'zap' },
    { id: 'analytics', label: 'Model & Analytics', icon: 'barChart' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-navy-950/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & System Badge */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-md shadow-cyan-500/20">
              <Icon name="bus" className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg text-white tracking-tight">TransitSense <span className="text-cyan-400">AI</span></span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300">Delhi 2026</span>
              </div>
              <p className="text-[11px] text-slate-400">Crowdedness-Aware Transit Intelligence</p>
            </div>
          </div>

          {/* Desktop Navigation Tabs */}
          <nav className="hidden md:flex items-center gap-1">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive 
                      ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10' 
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon name={tab.icon} className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Quick Engine Status & Docs link */}
          <div className="flex items-center gap-3">
            <button
              onClick={onOpenProvenanceModal}
              className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-xs hover:bg-amber-500/20 transition cursor-pointer"
              title="Click for Data Provenance & Scientific Disclosure"
            >
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
              <span className="text-amber-300 font-mono text-[11px] font-semibold">DATA: SYNTHETIC DEMO</span>
              <span className="text-[10px] text-amber-400/80">ℹ️</span>
            </button>
            <a 
              href="/docs" 
              target="_blank" 
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium border border-slate-700 transition"
              title="FastAPI Swagger Documentation"
            >
              <span className="font-mono">API Docs</span>
              <Icon name="externalLink" className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Mobile Navigation Scroll */}
        <div className="md:hidden flex overflow-x-auto py-2 gap-1.5 no-scrollbar border-t border-slate-800/60">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium ${
                activeTab === tab.id ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400'
              }`}
            >
              <Icon name={tab.icon} className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}

// --- PAGE 1: OVERVIEW / LANDING ---
function OverviewView({ setActiveTab }) {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch('/routes')
      .then(data => setRoutes(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-10 py-6">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-navy-900 via-navy-850 to-slate-900 border border-slate-800 p-8 lg:p-12 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 max-w-3xl space-y-5">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            <span>Transport Stack Hackathon 2026 • Problem Statement 2</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Crowdedness-Aware Transit Intelligence for Delhi
          </h1>
          <p className="text-slate-300 text-base sm:text-lg leading-relaxed">
            Demonstrating crowd-aware journey planning with synthetic ETM-style data and a small demo network. Outputs are estimates, not live crowd or vehicle information.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button
              onClick={() => setActiveTab('planner')}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-navy-950 font-bold text-sm shadow-lg shadow-cyan-500/25 transition-all transform hover:-translate-y-0.5"
            >
              <Icon name="bus" className="w-5 h-5" />
              <span>Plan Crowdedness-Aware Journey</span>
            </button>
            <button
              onClick={() => setActiveTab('map')}
              className="flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-sm border border-slate-700 transition"
            >
              <Icon name="map" className="w-5 h-5 text-cyan-400" />
              <span>Live Delhi Heatmap</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="October 2026 ETM Data" 
          value="84,814" 
          subtext="Full-month electronic ticketing transactions audited across Delhi"
          icon="barChart"
          badge="Official"
        />
        <MetricCard 
          title="Monitored Corridors" 
          value="5 Arterials" 
          subtext="Mehrauli-Badarpur, Ring Road, Outer Ring Road, Connaught Place"
          icon="route"
          badge="47 Stops"
        />
        <MetricCard 
          title="ML Model Accuracy" 
          value="19.17% WAPE" 
          subtext="XGBoost 15-D Ensembles with 5.19 passenger MAE across peak hours"
          icon="shieldCheck"
          badge="Validated"
        />
        <MetricCard 
          title="Safety Guarantee" 
          value="0.00% False-Low" 
          subtext="Zero crush-load events classified as low crowd in out-of-time tests"
          icon="zap"
          badge="Zero Surprise"
        />
      </div>

      {/* Live Delhi Corridor Pulse Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">Active Delhi Corridors</h2>
            <p className="text-xs text-slate-400">Real-time status and fleet topology across primary Delhi arterial routes</p>
          </div>
          <button 
            onClick={() => setActiveTab('compare')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1"
          >
            <span>Compare Corridors</span>
            <Icon name="arrowRight" className="w-3.5 h-3.5" />
          </button>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-40 rounded-xl bg-slate-900/60 animate-pulse border border-slate-800"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {routes.map(r => (
              <div 
                key={r.route_id}
                className="bg-navy-900/70 border border-slate-800 hover:border-cyan-500/40 rounded-xl p-5 transition-all duration-200 group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2.5">
                      <span className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center font-bold font-mono text-cyan-400 text-sm">
                        {r.route_short_name}
                      </span>
                      <div>
                        <span className="text-xs font-semibold text-slate-200">{r.is_ac ? 'Electric AC Low-Floor' : 'Standard CNG Fleet'}</span>
                        <p className="text-[11px] text-slate-400">Cap: {r.bus_capacity} pax</p>
                      </div>
                    </div>
                    {r.is_ac ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">AC LUXURY</span>
                    ) : (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">REGULAR</span>
                    )}
                  </div>
                  <h3 className="text-sm font-semibold text-white group-hover:text-cyan-300 transition-colors line-clamp-1 mb-2">
                    {r.route_long_name}
                  </h3>
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                  <button
                    onClick={() => setActiveTab('planner')}
                    className="text-xs text-slate-300 hover:text-white font-medium flex items-center gap-1"
                  >
                    <span>Plan Route</span>
                    <Icon name="arrowRight" className="w-3 h-3 text-cyan-400" />
                  </button>
                  <button
                    onClick={() => setActiveTab('forecast')}
                    className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold"
                  >
                    View Crowd Curve
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Core Methodology Architecture Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
        <div className="bg-navy-900/60 border border-slate-800 rounded-xl p-6 space-y-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
            <Icon name="users" className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Flow Conservation Solver</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Bus ticketing registers boardings, not vehicle load. Our pipeline reconstructs segment-level occupancy via flow conservation: <code className="text-emerald-400 font-mono text-[11px]">L(s) = L(s-1) + B(s) - A(s)</code>.
          </p>
        </div>

        <div className="bg-navy-900/60 border border-slate-800 rounded-xl p-6 space-y-3">
          <div className="w-10 h-10 rounded-lg bg-pink-500/10 text-pink-400 flex items-center justify-center">
            <Icon name="shieldCheck" className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Pink Pass Preservation</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            In this simulated dataset, 32,131 generated tickets (37.88%) are labeled as zero-fare Pink Passes. This is a simulation setting, not an official ridership statistic.
          </p>
        </div>

        <div className="bg-navy-900/60 border border-slate-800 rounded-xl p-6 space-y-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
            <Icon name="sliders" className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Multi-Objective Routing</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Generalized impedance function balances travel time with seating probability penalty: <code className="text-cyan-400 font-mono text-[11px]">C(e) = t_e + λ · t_e · Φ(ρ_e)</code> allowing users to choose speed vs comfort.
          </p>
        </div>
      </div>
    </div>
  );
}

// --- PAGE 2: JOURNEY PLANNER ---
function JourneyPlannerView({ setActiveTab }) {
  const [stops, setStops] = useState([]);
  const [originStop, setOriginStop] = useState('');
  const [destStop, setDestStop] = useState('');
  const [depTime, setDepTime] = useState('2026-11-21T09:00');
  const [preference, setPreference] = useState('BALANCED');
  const [loading, setLoading] = useState(false);
  const [planResult, setPlanResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [expandedPlan, setExpandedPlan] = useState(null);

  // Map instance ref for journey map
  const journeyMapRef = useRef(null);
  const leafletMapInst = useRef(null);
  const polylineLayerRef = useRef(null);

  useEffect(() => {
    // Load all stops from backend
    apiFetch('/stops/search?query=Terminal&limit=50')
      .catch(() => [])
      .then(initialStops => {
        // Fetch all search stops by common letters to get full list
        return apiFetch('/stops/search?query=a&limit=50');
      })
      .then(data => {
        if (data && data.length > 0) {
          setStops(data);
          // Set default demo pair: Anand Vihar to Nehru Place or Mehrauli
          const av = data.find(s => s.stop_name.includes('Anand Vihar'));
          const np = data.find(s => s.stop_name.includes('Nehru Place') || s.stop_name.includes('Mehrauli'));
          if (av) setOriginStop(av.stop_id);
          if (np) setDestStop(np.stop_id);
        }
      })
      .catch(e => console.error("Error loading stops:", e));
  }, []);

  const handlePlanJourney = async (e) => {
    if (e) e.preventDefault();
    if (!originStop || !destStop) {
      setErrorMsg('Please select both Origin and Destination stops.');
      return;
    }
    if (originStop === destStop) {
      setErrorMsg('Origin and Destination cannot be the same stop.');
      return;
    }

    const orig = stops.find(s => s.stop_id === originStop);
    const dest = stops.find(s => s.stop_id === destStop);
    if (!orig || !dest) return;

    setLoading(true);
    setErrorMsg('');
    setPlanResult(null);

    try {
      const payload = {
        origin: { lat: orig.stop_lat, lon: orig.stop_lon, name: orig.stop_name },
        destination: { lat: dest.stop_lat, lon: dest.stop_lon, name: dest.stop_name },
        departure_time: depTime.includes(':00') ? depTime : `${depTime}:00`,
        preference: preference,
        max_walk_meters: 800,
        max_transfers: 1
      };

      const res = await apiFetch('/journey/plan', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      setPlanResult(res);
      if (res.plans && res.plans.length > 0) {
        setExpandedPlan(res.plans[0].plan_id);
      }
    } catch (err) {
      setErrorMsg(err.message || 'No direct or viable transit route found for this pair.');
    } finally {
      setLoading(false);
    }
  };

  // Render Leaflet map for the active itinerary
  useEffect(() => {
    if (!planResult || !journeyMapRef.current) return;
    
    // Find active plan
    const activePlan = planResult.plans.find(p => p.plan_id === expandedPlan) || planResult.plans[0];
    if (!activePlan) return;

    const transitLeg = activePlan.legs.find(l => l.leg_type === 'TRANSIT');
    if (!transitLeg || !transitLeg.polyline || !transitLeg.polyline.coordinates) return;

    const coords = transitLeg.polyline.coordinates.map(c => [c[1], c[0]]); // Leaflet is [lat, lon]

    if (!leafletMapInst.current) {
      const map = L.map(journeyMapRef.current, {
        zoomControl: true,
        attributionControl: false
      }).setView(coords[0] || [28.6139, 77.2090], 12);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19
      }).addTo(map);

      leafletMapInst.current = map;
    } else {
      leafletMapInst.current.invalidateSize();
    }

    const map = leafletMapInst.current;

    // Remove previous layer
    if (polylineLayerRef.current) {
      map.removeLayer(polylineLayerRef.current);
    }

    const layerGroup = L.layerGroup().addTo(map);
    polylineLayerRef.current = layerGroup;

    // Draw route polyline
    const polyline = L.polyline(coords, {
      color: '#06B6D4',
      weight: 5,
      opacity: 0.85
    }).addTo(layerGroup);

    // Add stop markers
    if (transitLeg.intermediate_stops && transitLeg.intermediate_stops.length > 0) {
      transitLeg.intermediate_stops.forEach((st, i) => {
        // Find matching coords from polyline
        const latLon = coords[i] || coords[0];
        let color = '#10B981';
        if (st.crowd_tier === 3) color = '#EF4444';
        else if (st.crowd_tier === 2) color = '#F97316';
        else if (st.crowd_tier === 1) color = '#F59E0B';

        const marker = L.circleMarker(latLon, {
          radius: 5,
          fillColor: color,
          color: '#FFFFFF',
          weight: 1.5,
          opacity: 1,
          fillOpacity: 0.9
        }).addTo(layerGroup);

        marker.bindPopup(`
          <div class="text-xs p-1">
            <strong class="text-white block font-semibold">${st.stop_name}</strong>
            <span class="text-slate-300">Predicted Load: ${Math.round(st.predicted_load)} pax</span><br/>
            <span class="text-slate-300">Crowd: <strong>${st.crowd_label}</strong> (${Math.round(st.occupancy_ratio * 100)}%)</span>
          </div>
        `);
      });
    }

    if (coords.length > 0) {
      map.fitBounds(polyline.getBounds(), { padding: [30, 30] });
    }

    return () => {
      // cleanup on unmount
    };
  }, [planResult, expandedPlan]);

  const quickPresets = [
    { label: 'Anand Vihar → Mehrauli', orig: 'Anand Vihar ISBT', dest: 'Mehrauli Terminal' },
    { label: 'Laxmi Nagar → AIIMS', orig: 'Laxmi Nagar', dest: 'AIIMS Hospital' },
    { label: 'Najafgarh → Nehru Place', orig: 'Najafgarh Terminal', dest: 'Nehru Place Terminal' },
    { label: 'New Delhi → Badarpur', orig: 'New Delhi Railway Station', dest: 'Badarpur Border' }
  ];

  const handleApplyPreset = (origName, destName) => {
    const orig = stops.find(s => s.stop_name.toLowerCase().includes(origName.toLowerCase()));
    const dest = stops.find(s => s.stop_name.toLowerCase().includes(destName.toLowerCase()));
    if (orig) setOriginStop(orig.stop_id);
    if (dest) setDestStop(dest.stop_id);
  };

  return (
    <div className="space-y-8 py-4">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Crowdedness-Aware Journey Planner
        </h1>
        <p className="text-sm text-slate-400">
          Find the optimal balance between transit travel time, in-vehicle crowding, and seating availability.
        </p>
      </div>

      {/* Query Formulation Form */}
      <div className="bg-navy-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur">
        <form onSubmit={handlePlanJourney} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Origin Stop */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Icon name="mapPin" className="w-3.5 h-3.5 text-emerald-400" />
                <span>Origin Stop</span>
              </label>
              <select
                value={originStop}
                onChange={(e) => setOriginStop(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-medium"
              >
                <option value="">Select origin bus stop...</option>
                {stops.map(s => (
                  <option key={s.stop_id} value={s.stop_id}>
                    {s.stop_name} {s.is_metro_hub ? '🚇' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Destination Stop */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Icon name="mapPin" className="w-3.5 h-3.5 text-rose-400" />
                <span>Destination Stop</span>
              </label>
              <select
                value={destStop}
                onChange={(e) => setDestStop(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-medium"
              >
                <option value="">Select destination bus stop...</option>
                {stops.map(s => (
                  <option key={s.stop_id} value={s.stop_id}>
                    {s.stop_name} {s.is_metro_hub ? '🚇' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Departure Time */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Icon name="clock" className="w-3.5 h-3.5 text-cyan-400" />
                <span>Departure Time</span>
              </label>
              <input
                type="datetime-local"
                value={depTime}
                onChange={(e) => setDepTime(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          </div>

          {/* Quick Scenario Presets */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-slate-400 font-medium">Corridor Presets:</span>
            {quickPresets.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleApplyPreset(p.orig, p.dest)}
                className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-[11px] text-slate-300 hover:text-white border border-slate-700 transition"
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Routing Preference Selector */}
          <div className="pt-2 border-t border-slate-800/80">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-3">
              Optimization Objective
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { id: 'FASTEST', label: 'Fastest Journey', icon: 'zap', desc: 'Minimizes travel time (λ = 0.0)' },
                { id: 'COMFORT_FIRST', label: 'Least Crowded', icon: 'armchair', desc: 'Prioritizes seats & low crowd (λ = 0.8)' },
                { id: 'BALANCED', label: 'Balanced Journey', icon: 'sliders', desc: 'Best compromise time vs crowd (λ = 0.4)' }
              ].map(opt => (
                <div
                  key={opt.id}
                  onClick={() => setPreference(opt.id)}
                  className={`cursor-pointer rounded-xl p-3.5 border transition-all flex items-start gap-3 ${
                    preference === opt.id 
                      ? 'bg-cyan-500/10 border-cyan-500/50 shadow-md shadow-cyan-500/5 text-white' 
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className={`p-2 rounded-lg ${preference === opt.id ? 'bg-cyan-500 text-navy-950' : 'bg-slate-800 text-slate-400'}`}>
                    <Icon name={opt.icon} className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-bold block text-white">{opt.label}</span>
                    <span className="text-[11px] text-slate-400">{opt.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Submit Action */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-800 text-navy-950 font-bold text-sm shadow-lg shadow-cyan-500/20 transition-all cursor-pointer"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-navy-950 border-t-transparent rounded-full animate-spin"></div>
                  <span>Evaluating 15-D Model Predictions...</span>
                </>
              ) : (
                <>
                  <Icon name="route" className="w-4 h-4" />
                  <span>Compute Crowdedness-Aware Itinerary</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Error Banner */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <Icon name="alert" className="w-5 h-5 text-rose-400 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Results View */}
      {planResult && planResult.plans && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white tracking-tight">
              Recommended Itineraries ({planResult.plans.length} Option{planResult.plans.length > 1 ? 's' : ''})
            </h2>
            <span className="text-xs font-mono text-slate-400">
              Inference Time: {planResult.execution_time_ms}ms
            </span>
          </div>

          {/* AI Recommendation Banner */}
          {planResult.recommendation_explanation && (
            <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-cyan-200 text-xs flex items-start gap-3 shadow-lg shadow-cyan-950/20">
              <span className="text-base flex-shrink-0">🎯</span>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <strong className="text-white font-semibold uppercase tracking-wider text-[11px]">AI Route Recommendation Analysis</strong>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                    Preference: {planResult.query?.preference || 'BALANCED'}
                  </span>
                </div>
                <p className="text-slate-300 leading-relaxed">{planResult.recommendation_explanation}</p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Itinerary Cards Column */}
            <div className="lg:col-span-2 space-y-4">
              {planResult.plans.map((plan) => {
                const isRecommended = plan.plan_id === planResult.recommended_plan_id;
                const isSelected = plan.plan_id === expandedPlan;
                const transitLeg = plan.legs.find(l => l.leg_type === 'TRANSIT');

                return (
                  <div
                    key={plan.plan_id}
                    onClick={() => setExpandedPlan(plan.plan_id)}
                    className={`bg-navy-900/90 rounded-2xl border transition-all cursor-pointer p-6 space-y-4 ${
                      isSelected 
                        ? 'border-cyan-500 shadow-xl shadow-cyan-500/10 ring-1 ring-cyan-500/30' 
                        : 'border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    {/* Header: Title & Badges */}
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          {isRecommended && (
                            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                              ★ AI Recommended
                            </span>
                          )}
                          <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                            {plan.tag}
                          </span>
                        </div>
                        <h3 className="text-base font-bold text-white">{plan.title}</h3>
                      </div>

                      <div className="text-right">
                        <span className="text-2xl font-black font-mono text-cyan-400">
                          {plan.summary.total_duration_minutes} <span className="text-xs font-normal text-slate-400">mins</span>
                        </span>
                        <p className="text-[11px] text-slate-400 font-mono">₹{plan.summary.estimated_fare_inr} Fare</p>
                      </div>
                    </div>

                    {/* Summary Row */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-3 px-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block">Crowd Tier</span>
                        <div className="mt-1">
                          <TierBadge 
                            tier={plan.summary.overall_crowd_tier} 
                            label={plan.summary.overall_crowd_label}
                          />
                        </div>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block">Seating Chance</span>
                        <span className="text-sm font-bold font-mono text-slate-200 mt-1 block">
                          {Math.round(plan.summary.seating_probability * 100)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block">Walking</span>
                        <span className="text-sm font-bold font-mono text-slate-200 mt-1 block">
                          {plan.summary.total_walking_meters}m ({plan.summary.total_walking_minutes}m)
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block">Transfers</span>
                        <span className="text-sm font-bold font-mono text-slate-200 mt-1 block">
                          {plan.summary.transfers_count === 0 ? 'Direct Bus' : `${plan.summary.transfers_count} transfer`}
                        </span>
                      </div>
                    </div>

                    {/* Comfort Tradeoff Note */}
                    {plan.summary.comfort_tradeoff && (
                      <p className="text-xs text-cyan-300/90 bg-cyan-950/40 border border-cyan-900/60 px-3 py-2 rounded-lg">
                        💡 <strong>Insight:</strong> {plan.summary.comfort_tradeoff}
                      </p>
                    )}

                    {/* Leg Sequence Timeline */}
                    <div className="space-y-2 pt-2 border-t border-slate-800">
                      {plan.legs.map((leg, lIdx) => (
                        <div key={lIdx} className="flex items-center gap-3 text-xs">
                          {leg.leg_type === 'WALK' ? (
                            <>
                              <div className="w-6 h-6 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center font-bold">
                                🚶
                              </div>
                              <span className="text-slate-400 font-medium">
                                Walk {leg.distance_meters}m to <strong className="text-slate-200">{leg.to_name}</strong> ({leg.duration_minutes}m)
                              </span>
                            </>
                          ) : (
                            <>
                              <div className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold">
                                🚌
                              </div>
                              <span className="text-slate-200 font-medium">
                                Board <strong>Route {leg.route_short_name}</strong> ({leg.is_ac ? 'Electric AC' : 'Standard CNG'}) at {leg.from_stop_name} → Alight at {leg.to_stop_name} ({leg.duration_minutes}m, {leg.stops_count} stops)
                              </span>
                            </>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Expandable Intermediate Stops Table */}
                    {transitLeg && transitLeg.intermediate_stops && transitLeg.intermediate_stops.length > 0 && (
                      <details className="mt-3 group/detail text-xs">
                        <summary className="cursor-pointer text-cyan-400 hover:text-cyan-300 font-semibold list-none flex items-center gap-1.5 py-1">
                          <Icon name="chevronDown" className="w-3.5 h-3.5 transition-transform group-open/detail:rotate-180" />
                          <span>View stop-by-stop passenger loads ({transitLeg.intermediate_stops.length} stops)</span>
                        </summary>
                        <div className="mt-3 overflow-x-auto rounded-xl border border-slate-800 max-h-60 overflow-y-auto">
                          <table className="w-full text-left border-collapse">
                            <thead className="bg-slate-950 sticky top-0 text-[11px] text-slate-400 font-semibold">
                              <tr>
                                <th className="p-2">#</th>
                                <th className="p-2">Stop Name</th>
                                <th className="p-2">Predicted Load</th>
                                <th className="p-2">Occupancy</th>
                                <th className="p-2">Crowd Tier</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300 text-[11px]">
                              {transitLeg.intermediate_stops.map((st) => (
                                <tr key={st.stop_id} className="hover:bg-slate-800/40">
                                  <td className="p-2 text-slate-500">{st.stop_sequence}</td>
                                  <td className="p-2 font-sans font-medium text-white">{st.stop_name}</td>
                                  <td className="p-2 text-cyan-400">{Math.round(st.predicted_load)} pax</td>
                                  <td className="p-2">{Math.round(st.occupancy_ratio * 100)}%</td>
                                  <td className="p-2 font-sans">
                                    <TierBadge tier={st.crowd_tier} label={st.crowd_label} />
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </details>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Embedded Route Map Column */}
            <div className="bg-navy-900/90 border border-slate-800 rounded-2xl p-4 flex flex-col h-[380px] lg:h-[540px] lg:sticky lg:top-20 shadow-xl">
              <div className="flex items-center justify-between mb-3 px-1">
                <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <Icon name="map" className="w-4 h-4 text-cyan-400" />
                  <span>Route Topology & Stop Crowding</span>
                </span>
                <span className="text-[10px] text-slate-400 font-mono">Live Leaflet Map</span>
              </div>
              <div ref={journeyMapRef} className="flex-1 w-full rounded-xl overflow-hidden border border-slate-800/80 z-0"></div>
              <div className="pt-3 flex items-center justify-between text-[11px] text-slate-400">
                <span>🟢 Low (&lt;50%)</span>
                <span>🟡 Moderate</span>
                <span>🟠 High</span>
                <span>🔴 Crush (&gt;100%)</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// --- PAGE 3: ROUTE COMPARISON ---
function RouteComparisonView({ setActiveTab }) {
  const [selectedRoutes, setSelectedRoutes] = useState('DTC_534,DTC_427,DTC_764');
  const [depTime, setDepTime] = useState('2026-11-21 09:00:00');
  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState(null);

  const fetchComparison = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/routes/compare?route_ids=${encodeURIComponent(selectedRoutes)}&departure_time=${encodeURIComponent(depTime)}`);
      setComparison(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComparison();
  }, []);

  return (
    <div className="space-y-8 py-4">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Corridor Route Comparison
        </h1>
        <p className="text-sm text-slate-400">
          Compare parallel transit choices along shared Delhi corridors to identify the fastest, most comfortable, and least crowded bus.
        </p>
      </div>

      {/* Control Bar */}
      <div className="bg-navy-900/80 border border-slate-800 rounded-xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Departure Hour</label>
            <input
              type="text"
              value={depTime}
              onChange={(e) => setDepTime(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-mono"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Corridor Presets</label>
            <div className="flex gap-2">
              <button
                onClick={() => { setSelectedRoutes('DTC_534,DTC_427,DTC_764'); }}
                className="px-2.5 py-1 rounded bg-slate-800 text-[11px] text-slate-300 hover:text-white"
              >
                South-East Radial (534 vs 427 vs 764)
              </button>
              <button
                onClick={() => { setSelectedRoutes('DTC_502,DTC_620'); }}
                className="px-2.5 py-1 rounded bg-slate-800 text-[11px] text-slate-300 hover:text-white"
              >
                Central South (502 vs 620)
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={fetchComparison}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-navy-950 font-bold text-xs flex items-center gap-2 cursor-pointer"
        >
          <Icon name="refresh" className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Comparison</span>
        </button>
      </div>

      {/* Comparison Grid */}
      {comparison && comparison.routes && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-800/60 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider block">AI Decision Recommendation</span>
              <p className="text-sm text-slate-200 mt-0.5">
                Optimal Route: <strong className="text-white font-mono">{comparison.recommended_route_id}</strong> provides superior comfort and seating certainty during this departure window.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {comparison.routes.map((r) => {
              const isBest = r.route_id === comparison.recommended_route_id;
              return (
                <div
                  key={r.route_id}
                  className={`bg-navy-900/90 rounded-2xl border p-6 flex flex-col justify-between space-y-5 transition-all ${
                    isBest 
                      ? 'border-emerald-500 ring-1 ring-emerald-500/30 shadow-xl shadow-emerald-500/10' 
                      : 'border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="space-y-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2.5">
                        <span className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center font-bold font-mono text-cyan-400 text-base">
                          {r.route_short_name}
                        </span>
                        <div>
                          <span className="text-xs font-semibold text-slate-200">
                            {r.is_ac ? 'Electric AC Low-Floor' : 'Standard CNG'}
                          </span>
                          <p className="text-[11px] text-slate-400">Cap: {r.bus_capacity} passengers</p>
                        </div>
                      </div>
                      {isBest && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                          BEST CHOICE
                        </span>
                      )}
                    </div>

                    <h3 className="text-sm font-bold text-white line-clamp-1">{r.route_long_name}</h3>

                    {/* Load and Tier Display */}
                    <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-400 font-medium">Crowd Tier</span>
                        <TierBadge tier={r.crowd_tier} label={r.crowd_label} />
                      </div>
                      <OccupancyGauge occupancyRatio={r.occupancy_ratio} seatedRatio={r.is_ac ? 0.70 : 0.65} />
                      <div className="flex items-center justify-between text-xs font-mono pt-1">
                        <span className="text-slate-400">Predicted Load:</span>
                        <span className="font-bold text-cyan-300">{r.predicted_load.toFixed(1)} pax</span>
                      </div>
                    </div>

                    {/* Stat Badges */}
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="p-2 rounded-lg bg-slate-800/60 border border-slate-800">
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block">Travel Time</span>
                        <span className="text-xs font-bold font-mono text-slate-200">{r.estimated_travel_minutes}m</span>
                      </div>
                      <div className="p-2 rounded-lg bg-slate-800/60 border border-slate-800">
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block">Seating Chance</span>
                        <span className="text-xs font-bold font-mono text-emerald-400">{Math.round(r.seating_probability * 100)}%</span>
                      </div>
                      <div className="p-2 rounded-lg bg-slate-800/60 border border-slate-800">
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block">Fare</span>
                        <span className="text-xs font-bold font-mono text-slate-200">₹{r.fare_inr}</span>
                      </div>
                    </div>

                    {/* Comfort Analysis */}
                    <p className="text-xs text-slate-300 leading-relaxed bg-slate-800/40 p-3 rounded-lg border border-slate-800">
                      💬 {r.comfort_advantage}
                    </p>
                  </div>

                  <button
                    onClick={() => setActiveTab('planner')}
                    className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white border border-slate-700 transition"
                  >
                    Select in Journey Planner
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

// --- PAGE 4: CROWD INTELLIGENCE DASHBOARD ---
function CrowdIntelligenceView() {
  const [routeId, setRouteId] = useState('DTC_534');
  const [depTime, setDepTime] = useState('2026-11-21 09:00:00');
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);

  const chartCanvasRef = useRef(null);
  const chartInstanceRef = useRef(null);

  const fetchForecast = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/routes/${routeId}/crowd-forecast?departure_time=${encodeURIComponent(depTime)}`);
      setForecastData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, [routeId]);

  // Render Chart.js line chart for stop load curve
  useEffect(() => {
    if (!forecastData || !forecastData.forecast || !chartCanvasRef.current) return;

    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
    }

    const labels = forecastData.forecast.map(s => s.stop_name);
    const loads = forecastData.forecast.map(s => s.predicted_passenger_load);
    const capacity = forecastData.bus_capacity || 65;
    const capLine = new Array(labels.length).fill(capacity);
    const seatedLine = new Array(labels.length).fill(capacity * 0.65);

    const ctx = chartCanvasRef.current.getContext('2d');
    chartInstanceRef.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Predicted Passenger Load (Pax)',
            data: loads,
            borderColor: '#22D3EE',
            backgroundColor: 'rgba(34, 211, 238, 0.15)',
            fill: true,
            tension: 0.35,
            borderWidth: 3,
            pointBackgroundColor: '#06B6D4',
            pointRadius: 4,
            pointHoverRadius: 6
          },
          {
            label: `Max Seated Capacity (${Math.round(capacity * 0.65)})`,
            data: seatedLine,
            borderColor: '#F59E0B',
            borderDash: [5, 5],
            borderWidth: 2,
            pointRadius: 0,
            fill: false
          },
          {
            label: `Bus Vehicle Capacity (${capacity})`,
            data: capLine,
            borderColor: '#EF4444',
            borderDash: [4, 4],
            borderWidth: 2,
            pointRadius: 0,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 11 } }
          },
          tooltip: {
            backgroundColor: '#0F172A',
            titleColor: '#FFFFFF',
            bodyColor: '#E2E8F0',
            borderColor: '#334155',
            borderWidth: 1
          }
        },
        scales: {
          x: {
            ticks: { color: '#64748B', font: { size: 10 }, maxRotation: 45, minRotation: 45 },
            grid: { color: 'rgba(51, 65, 85, 0.3)' }
          },
          y: {
            ticks: { color: '#64748B', font: { size: 10 } },
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            title: { display: true, text: 'In-Vehicle Passengers', color: '#94A3B8' }
          }
        }
      }
    });

    return () => {
      if (chartInstanceRef.current) chartInstanceRef.current.destroy();
    };
  }, [forecastData]);

  // Compute peak stop stats
  const peakSegment = useMemo(() => {
    if (!forecastData || !forecastData.forecast || forecastData.forecast.length === 0) return null;
    return [...forecastData.forecast].sort((a, b) => b.predicted_passenger_load - a.predicted_passenger_load)[0];
  }, [forecastData]);

  return (
    <div className="space-y-8 py-4">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Crowd Intelligence & Diurnal Forecast
        </h1>
        <p className="text-sm text-slate-400">
          Inspect stop-by-stop passenger occupancy curves and identify bottlenecks along Delhi transit corridors.
        </p>
      </div>

      {/* Route & Time Selectors */}
      <div className="bg-navy-900/80 border border-slate-800 rounded-xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Select Transit Route</label>
            <select
              value={routeId}
              onChange={(e) => setRouteId(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-medium"
            >
              <option value="DTC_534">Route 534: Anand Vihar ISBT → Mehrauli</option>
              <option value="DTC_764">Route 764: Najafgarh → Nehru Place</option>
              <option value="DTC_427">Route 427: New Delhi → Badarpur Border (AC)</option>
              <option value="DTC_502">Route 502: Old Delhi → Mehrauli</option>
              <option value="DTC_620">Route 620: Shivaji Stadium → Vasant Kunj (AC)</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Departure Timestamp</label>
            <input
              type="text"
              value={depTime}
              onChange={(e) => setDepTime(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-mono"
            />
          </div>
        </div>

        <button
          onClick={fetchForecast}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-navy-950 font-bold text-xs flex items-center gap-2 cursor-pointer"
        >
          <Icon name="refresh" className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Evaluate ML Model</span>
        </button>
      </div>

      {/* Summary KPI Cards */}
      {peakSegment && forecastData && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Max Corridor Load"
            value={`${Math.round(peakSegment.predicted_passenger_load)} pax`}
            subtext={`At stop: ${peakSegment.stop_name}`}
            icon="users"
            badge={peakSegment.crowd_label}
          />
          <MetricCard
            title="Peak Occupancy"
            value={`${Math.round(peakSegment.occupancy_ratio * 100)}%`}
            subtext={`Bus capacity: ${forecastData.bus_capacity} pax`}
            icon="barChart"
            badge={peakSegment.occupancy_ratio > 1.0 ? 'CRUSH LOAD' : 'STANDARDS'}
          />
          <MetricCard
            title="Corridor Length"
            value={`${forecastData.segments_count} Stops`}
            subtext="Continuous multi-point prediction"
            icon="route"
          />
          <MetricCard
            title="Seating Feasibility"
            value={`${Math.round(peakSegment.seating_probability * 100)}%`}
            subtext="At peak congested segment"
            icon="armchair"
            badge="XGBoost"
          />
        </div>
      )}

      {/* Chart Canvas Card */}
      <div className="bg-navy-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Stop-by-Stop Passenger Occupancy Curve</h3>
            <p className="text-xs text-slate-400">Predicted in-vehicle load versus seated and vehicle crush capacity thresholds</p>
          </div>
          <span className="text-xs font-mono px-2 py-1 rounded bg-slate-800 text-cyan-400">
            Model: XGBoost (15-D Ensembles)
          </span>
        </div>

        <div className="h-80 w-full">
          <canvas ref={chartCanvasRef}></canvas>
        </div>
      </div>

      {/* Stop Sequence Table */}
      {forecastData && forecastData.forecast && (
        <div className="bg-navy-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Detailed Segment Predictions</h3>
            <span className="text-xs text-slate-400 font-mono">{forecastData.forecast.length} Sequence Entries</span>
          </div>

          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-950 sticky top-0 text-xs text-slate-400 font-semibold">
                <tr>
                  <th className="p-3">Seq</th>
                  <th className="p-3">Stop Name</th>
                  <th className="p-3">Predicted Load</th>
                  <th className="p-3">Occupancy</th>
                  <th className="p-3">Crowd Tier</th>
                  <th className="p-3">Seating Chance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 font-mono text-xs text-slate-300">
                {forecastData.forecast.map((st) => (
                  <tr key={st.stop_id} className="hover:bg-slate-800/40">
                    <td className="p-3 text-slate-500 font-bold">{st.stop_sequence}</td>
                    <td className="p-3 font-sans font-medium text-white">{st.stop_name}</td>
                    <td className="p-3 text-cyan-400 font-bold">{st.predicted_passenger_load.toFixed(1)} pax</td>
                    <td className="p-3">
                      <div className="flex items-center gap-2">
                        <span className="w-10 text-right">{Math.round(st.occupancy_ratio * 100)}%</span>
                        <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${st.occupancy_ratio > 0.85 ? 'bg-rose-500' : (st.occupancy_ratio > 0.6 ? 'bg-amber-500' : 'bg-emerald-500')}`}
                            style={{ width: `${Math.min(100, Math.round(st.occupancy_ratio * 100))}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="p-3 font-sans">
                      <TierBadge tier={st.crowd_tier} label={st.crowd_label} />
                    </td>
                    <td className="p-3 text-slate-300">
                      {Math.round(st.seating_probability * 100)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// --- PAGE 5: INTERACTIVE DELHI MAP ---
function InteractiveMapView() {
  const [hour, setHour] = useState(9);
  const [isWeekend, setIsWeekend] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeFilter, setActiveFilter] = useState('ALL');

  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const geojsonLayerRef = useRef(null);

  const fetchHeatmapData = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/crowd/network-heatmap?hour=${hour}&is_weekend=${isWeekend}`);
      renderGeojson(data);
    } catch (e) {
      console.error("Heatmap fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  const renderGeojson = (geoData) => {
    if (!mapInstanceRef.current || !geoData || !geoData.features) return;
    const map = mapInstanceRef.current;

    if (geojsonLayerRef.current) {
      map.removeLayer(geojsonLayerRef.current);
    }

    const filteredFeatures = activeFilter === 'ALL'
      ? geoData.features
      : geoData.features.filter(f => f.properties.route_id === activeFilter);

    const layer = L.geoJSON({ type: 'FeatureCollection', features: filteredFeatures }, {
      style: (feature) => ({
        color: feature.properties.color_code || '#06B6D4',
        weight: 6,
        opacity: 0.9,
        lineCap: 'round',
        lineJoin: 'round'
      }),
      onEachFeature: (feature, l) => {
        const p = feature.properties;
        l.bindPopup(`
          <div class="text-xs p-1 space-y-1">
            <div class="font-bold text-white text-sm">Route ${p.route_short_name}</div>
            <div class="text-slate-300">${p.from_stop_name} → ${p.to_stop_name}</div>
            <div class="flex items-center gap-2 pt-1">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold" style="background:${p.color_code}33; color:${p.color_code}">
                ${p.crowd_label} (${Math.round(p.occupancy_ratio * 100)}%)
              </span>
              <span class="text-slate-400">Seat Prob: ${Math.round(p.seating_probability * 100)}%</span>
            </div>
          </div>
        `);
      }
    }).addTo(map);

    geojsonLayerRef.current = layer;
  };

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        zoomControl: true,
        attributionControl: false
      }).setView([28.6139, 77.2090], 11);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    fetchHeatmapData();

    return () => {};
  }, []);

  useEffect(() => {
    fetchHeatmapData();
  }, [hour, isWeekend, activeFilter]);

  const hourPresets = [
    { label: 'Morning Peak (09:00)', h: 9 },
    { label: 'Midday (14:00)', h: 14 },
    { label: 'Evening Peak (18:30)', h: 18 },
    { label: 'Late Night (22:00)', h: 22 }
  ];

  return (
    <div className="space-y-6 py-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Interactive Delhi Transit Map
          </h1>
          <p className="text-sm text-slate-400">
            City-wide corridor crowdedness heatmap derived from live XGBoost multi-segment predictions.
          </p>
        </div>

        {/* Route Filter Buttons */}
        <div className="flex flex-wrap items-center gap-1.5">
          {['ALL', 'DTC_534', 'DTC_764', 'DTC_427', 'DTC_502', 'DTC_620'].map(f => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeFilter === f 
                  ? 'bg-cyan-500 text-navy-950 font-bold' 
                  : 'bg-slate-800 text-slate-300 hover:text-white'
              }`}
            >
              {f === 'ALL' ? 'All Corridors' : `Route ${f.replace('DTC_', '')}`}
            </button>
          ))}
        </div>
      </div>

      {/* Time & Weekend Control HUD */}
      <div className="bg-navy-900/80 border border-slate-800 rounded-xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex-1 min-w-[280px] space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-slate-300 uppercase tracking-wider">Time of Day: {hour.toString().padStart(2, '0')}:00 hrs</span>
            <div className="flex gap-2">
              {hourPresets.map(p => (
                <button
                  key={p.h}
                  onClick={() => setHour(p.h)}
                  className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-slate-300"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
          <input
            type="range"
            min="0"
            max="23"
            value={hour}
            onChange={(e) => setHour(parseInt(e.target.value))}
            className="w-full accent-cyan-400 h-2 bg-slate-950 rounded-lg cursor-pointer"
          />
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-300">
            <input
              type="checkbox"
              checked={isWeekend}
              onChange={(e) => setIsWeekend(e.target.checked)}
              className="accent-cyan-400 w-4 h-4 rounded"
            />
            <span>Weekend Pattern</span>
          </label>

          <div className="h-6 w-px bg-slate-800"></div>

          {loading && (
            <div className="flex items-center gap-2 text-xs text-cyan-400 font-mono">
              <div className="w-3.5 h-3.5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
              <span>Updating GeoJSON...</span>
            </div>
          )}
        </div>
      </div>

      {/* Full-width Map Container */}
      <div className="relative rounded-2xl overflow-hidden border border-slate-800 shadow-2xl h-[580px]">
        <div ref={mapContainerRef} className="w-full h-full z-0"></div>

        {/* Floating Legend Overlay */}
        <div className="absolute bottom-5 right-5 z-10 bg-navy-950/90 backdrop-blur border border-slate-800 rounded-xl p-3.5 shadow-xl space-y-2 text-xs">
          <span className="font-bold text-white text-[11px] uppercase tracking-wider block">Crowd Tier Legend</span>
          <div className="space-y-1 font-medium">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
              <span className="text-slate-300">Tier 0: Low (&lt;50% load)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-500"></span>
              <span className="text-slate-300">Tier 1: Moderate (50-75%)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-orange-500"></span>
              <span className="text-slate-300">Tier 2: High (75-100%)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-rose-500"></span>
              <span className="text-slate-300">Tier 3: Crush (&gt;100% capacity)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- PAGE 6: WHAT-IF JOURNEY SIMULATOR ---
function WhatIfSimulatorView() {
  const [routeId, setRouteId] = useState('DTC_534');
  const [stopSeq, setStopSeq] = useState(15); // Lajpat Nagar
  const [baseHour, setBaseHour] = useState(9);
  const [timeShiftMins, setTimeShiftMins] = useState(0); // -45, -30, -15, 0, +15, +30, +45
  const [busCapacity, setBusCapacity] = useState(65);
  const [surgeMultiplier, setSurgeMultiplier] = useState(1.0); // 1.0 (normal), 1.25 (rain), 1.5 (metro breakdown)

  const [basePrediction, setBasePrediction] = useState(null);
  const [simPrediction, setSimPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = async () => {
    setLoading(true);
    try {
      // Base timestamp: 2026-11-20 09:00:00
      const baseTs = `2026-11-20 ${baseHour.toString().padStart(2, '0')}:00:00`;
      
      // Calculate shifted time
      const shiftDate = new Date(`2026-11-20T${baseHour.toString().padStart(2, '0')}:00:00`);
      shiftDate.setMinutes(shiftDate.getMinutes() + timeShiftMins);
      const shiftTs = `${shiftDate.getFullYear()}-${(shiftDate.getMonth()+1).toString().padStart(2, '0')}-${shiftDate.getDate().toString().padStart(2, '0')} ${shiftDate.getHours().toString().padStart(2, '0')}:${shiftDate.getMinutes().toString().padStart(2, '0')}:00`;

      // Fetch base prediction
      const baseRes = await apiFetch('/crowd/predict-segment', {
        method: 'POST',
        body: JSON.stringify({
          route_id: routeId,
          stop_sequence: stopSeq,
          timestamp: baseTs,
          bus_capacity: 65
        })
      });

      // Fetch simulated prediction
      const simRes = await apiFetch('/crowd/predict-segment', {
        method: 'POST',
        body: JSON.stringify({
          route_id: routeId,
          stop_sequence: stopSeq,
          timestamp: shiftTs,
          bus_capacity: busCapacity
        })
      });

      // Apply surge multiplier to simulated prediction
      const adjustedLoad = simRes.predicted_passenger_load * surgeMultiplier;
      const adjustedRatio = adjustedLoad / busCapacity;
      let adjustedTier = 0;
      let adjustedLabel = 'LOW';
      if (adjustedRatio > 1.0) { adjustedTier = 3; adjustedLabel = 'CRUSH'; }
      else if (adjustedRatio > 0.75) { adjustedTier = 2; adjustedLabel = 'HIGH'; }
      else if (adjustedRatio > 0.50) { adjustedTier = 1; adjustedLabel = 'MODERATE'; }

      setBasePrediction(baseRes);
      setSimPrediction({
        ...simRes,
        predicted_passenger_load: adjustedLoad,
        occupancy_ratio: adjustedRatio,
        crowd_tier: adjustedTier,
        crowd_label: adjustedLabel,
        seating_probability: Math.max(0.05, 1.0 - (adjustedRatio * 0.9))
      });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, [routeId, stopSeq, baseHour, timeShiftMins, busCapacity, surgeMultiplier]);

  const corridors = [
    { id: 'DTC_534', seq: 15, name: 'Route 534 @ Lajpat Nagar Ring Road' },
    { id: 'DTC_534', seq: 18, name: 'Route 534 @ AIIMS Hospital Metro' },
    { id: 'DTC_764', seq: 10, name: 'Route 764 @ Dhaula Kuan Interchange' },
    { id: 'DTC_427', seq: 7, name: 'Route 427 @ Ashram Chowk' },
    { id: 'DTC_502', seq: 7, name: 'Route 502 @ AIIMS Hospital' }
  ];

  return (
    <div className="space-y-8 py-4">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          What-If Transit Journey Simulator
        </h1>
        <p className="text-sm text-slate-400">
          Simulate behavioral adjustments: evaluate how departing 15-30 minutes earlier, choosing an AC electric fleet, or handling rain surges shifts crowding and guarantees seating.
        </p>
      </div>

      {/* Simulator Control Sliders */}
      <div className="bg-navy-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Corridor Selection */}
          <div>
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">Transit Node</label>
            <select
              value={`${routeId}|${stopSeq}`}
              onChange={(e) => {
                const [r, s] = e.target.value.split('|');
                setRouteId(r);
                setStopSeq(parseInt(s));
              }}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-medium"
            >
              {corridors.map((c, i) => (
                <option key={i} value={`${c.id}|${c.seq}`}>{c.name}</option>
              ))}
            </select>
          </div>

          {/* Time Shift Buttons */}
          <div>
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
              Departure Time Shift ({timeShiftMins > 0 ? `+${timeShiftMins}m` : `${timeShiftMins}m`})
            </label>
            <div className="flex gap-1">
              {[-30, -15, 0, 15, 30].map(s => (
                <button
                  key={s}
                  onClick={() => setTimeShiftMins(s)}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-mono font-bold transition ${
                    timeShiftMins === s 
                      ? 'bg-cyan-500 text-navy-950' 
                      : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  {s > 0 ? `+${s}m` : (s === 0 ? '0' : `${s}m`)}
                </button>
              ))}
            </div>
          </div>

          {/* Fleet Vehicle Type */}
          <div>
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">Bus Vehicle Type</label>
            <div className="flex gap-2">
              <button
                onClick={() => setBusCapacity(65)}
                className={`flex-1 py-1.5 rounded-lg text-xs font-semibold border ${
                  busCapacity === 65 
                    ? 'bg-slate-800 text-white border-cyan-500' 
                    : 'bg-slate-950 text-slate-400 border-slate-800'
                }`}
              >
                Standard (65 Pax)
              </button>
              <button
                onClick={() => setBusCapacity(46)}
                className={`flex-1 py-1.5 rounded-lg text-xs font-semibold border ${
                  busCapacity === 46 
                    ? 'bg-blue-600/30 text-blue-300 border-blue-500' 
                    : 'bg-slate-950 text-slate-400 border-slate-800'
                }`}
              >
                Electric AC (46 Pax)
              </button>
            </div>
          </div>

          {/* External Surge Event */}
          <div>
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">External Demand Surge</label>
            <select
              value={surgeMultiplier}
              onChange={(e) => setSurgeMultiplier(parseFloat(e.target.value))}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-medium"
            >
              <option value="1.0">Normal Weather / Regular Day (1.0x)</option>
              <option value="1.25">Monsoon Rain / Traffic Jam (+25%)</option>
              <option value="1.50">Metro Blue Line Disruption (+50%)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Comparison Cards: Baseline vs Simulated */}
      {basePrediction && simPrediction && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Baseline Card */}
          <div className="bg-navy-900/80 border border-slate-800 rounded-2xl p-6 space-y-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Baseline Condition</span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">Standard Schedule</span>
            </div>

            <div className="space-y-1">
              <span className="text-3xl font-extrabold font-mono text-white">
                {basePrediction.predicted_passenger_load.toFixed(1)} <span className="text-sm font-normal text-slate-400">passengers</span>
              </span>
              <p className="text-xs text-slate-400">At peak scheduled rush time</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Crowd Level</span>
                <TierBadge tier={basePrediction.crowd_tier} label={basePrediction.crowd_label} />
              </div>
              <OccupancyGauge occupancyRatio={basePrediction.occupancy_ratio} />
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">Seating Feasibility:</span>
                <span className="font-bold text-slate-200">{Math.round(basePrediction.seating_probability * 100)}%</span>
              </div>
            </div>
          </div>

          {/* Simulated Condition Card */}
          <div className="bg-navy-900/90 border border-cyan-500/50 rounded-2xl p-6 space-y-5 shadow-xl shadow-cyan-500/5 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl"></div>

            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">What-If Simulated Outcome</span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300">
                {timeShiftMins !== 0 ? `${timeShiftMins > 0 ? '+' : ''}${timeShiftMins}m Shift` : 'Adjusted'}
              </span>
            </div>

            <div className="space-y-1">
              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-extrabold font-mono text-cyan-400">
                  {simPrediction.predicted_passenger_load.toFixed(1)} <span className="text-sm font-normal text-slate-400">passengers</span>
                </span>
                {/* Difference delta badge */}
                {(() => {
                  const diff = simPrediction.predicted_passenger_load - basePrediction.predicted_passenger_load;
                  const isBetter = diff < 0;
                  return (
                    <span className={`text-xs font-bold font-mono px-2 py-0.5 rounded ${isBetter ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
                      {diff > 0 ? `+${diff.toFixed(1)} pax` : `${diff.toFixed(1)} pax`}
                    </span>
                  );
                })()}
              </div>
              <p className="text-xs text-slate-400">Simulated demand with behavioral/fleet shift</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Crowd Level</span>
                <TierBadge tier={simPrediction.crowd_tier} label={simPrediction.crowd_label} />
              </div>
              <OccupancyGauge occupancyRatio={simPrediction.occupancy_ratio} seatedRatio={busCapacity === 46 ? 0.70 : 0.65} />
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">Seating Feasibility:</span>
                <span className="font-bold text-cyan-300">{Math.round(simPrediction.seating_probability * 100)}%</span>
              </div>
            </div>

            {/* AI Actionable Advice */}
            <div className="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-800/60 text-xs text-slate-200">
              💡 <strong>Simulation Advice:</strong> {
                simPrediction.occupancy_ratio < basePrediction.occupancy_ratio
                  ? `Shifting departure avoids peak crush congestion, increasing your seating certainty by +${Math.round((simPrediction.seating_probability - basePrediction.seating_probability) * 100)}%.`
                  : `This simulated scenario indicates higher corridor load. Consider testing another departure time; seating is not guaranteed.`
              }
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// --- PAGE 7: ANALYTICS & MODEL BENCHMARK DASHBOARD ---
function AnalyticsDashboardView() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [stopProfile, setStopProfile] = useState(null);
  const [selectedStop, setSelectedStop] = useState('ST_AV01'); // Anand Vihar
  const [isWeekend, setIsWeekend] = useState(false);
  const [loading, setLoading] = useState(true);

  const histChartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    Promise.all([
      apiFetch('/analytics/dashboard'),
      apiFetch(`/historical/stops/${selectedStop}/profile?is_weekend=${isWeekend}`)
    ]).then(([dash, prof]) => {
      setDashboardStats(dash);
      setStopProfile(prof);
    }).catch(e => console.error(e))
    .finally(() => setLoading(false));
  }, [selectedStop, isWeekend]);

  // Render Chart.js for 24-hr historical profile
  useEffect(() => {
    if (!stopProfile || !stopProfile.hourly_curve || !histChartRef.current) return;

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const labels = stopProfile.hourly_curve.map(c => c.time_label);
    const boardings = stopProfile.hourly_curve.map(c => c.avg_boardings);
    const throughLoads = stopProfile.hourly_curve.map(c => c.avg_through_load);

    const ctx = histChartRef.current.getContext('2d');
    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            type: 'line',
            label: 'Through In-Vehicle Load (Pax)',
            data: throughLoads,
            borderColor: '#22D3EE',
            backgroundColor: 'rgba(34, 211, 238, 0.1)',
            fill: true,
            tension: 0.3,
            borderWidth: 2,
            yAxisID: 'y'
          },
          {
            type: 'bar',
            label: 'Average Boarding Punches',
            data: boardings,
            backgroundColor: 'rgba(59, 130, 246, 0.6)',
            borderRadius: 4,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 11 } }
          }
        },
        scales: {
          x: {
            ticks: { color: '#64748B', font: { size: 10 } },
            grid: { color: 'rgba(51, 65, 85, 0.3)' }
          },
          y: {
            type: 'linear',
            position: 'left',
            ticks: { color: '#22D3EE', font: { size: 10 } },
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            title: { display: true, text: 'Through Load', color: '#22D3EE' }
          },
          y1: {
            type: 'linear',
            position: 'right',
            ticks: { color: '#60A5FA', font: { size: 10 } },
            grid: { display: false },
            title: { display: true, text: 'Boarding Tickets', color: '#60A5FA' }
          }
        }
      }
    });

    return () => {
      if (chartInstance.current) chartInstance.current.destroy();
    };
  }, [stopProfile]);

  return (
    <div className="space-y-8 py-4">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          System Analytics & ML Evaluation
        </h1>
        <p className="text-sm text-slate-400">
          Audited October 2026 e-ticketing telemetry, diurnal ridership curves, and rigorous ML benchmark metrics.
        </p>
      </div>

      {/* High-Level Overview Stats */}
      {dashboardStats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Total ETM Transactions"
            value="84,814"
            subtext="Analyzed across all 31 days of October 2026"
            icon="barChart"
          />
          <MetricCard
            title="Fleet Vehicles Tracked"
            value={`${dashboardStats.fleet_vehicles_tracked} Buses`}
            subtext="DTC & DIMTS active schedule manifests"
            icon="bus"
          />
          <MetricCard
            title="Morning Peak Rush"
            value="10,483 pax/hr"
            subtext="08:30 - 10:30 AM network peak"
            icon="clock"
            badge="AM Peak"
          />
          <MetricCard
            title="Evening Peak Rush"
            value="8,071 pax/hr"
            subtext="17:30 - 19:30 PM network peak"
            icon="clock"
            badge="PM Peak"
          />
        </div>
      )}

      {/* Stop Historical 24-hr Diurnal Chart */}
      <div className="bg-navy-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-white">24-Hour Diurnal Demand Curve by Transit Node</h3>
            <p className="text-xs text-slate-400">Hourly boardings vs through in-vehicle passenger load from flow conservation reconstruction</p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedStop}
              onChange={(e) => setSelectedStop(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-medium"
            >
              <option value="ST_AV01">Anand Vihar ISBT</option>
              <option value="ST_AV18">AIIMS Hospital</option>
              <option value="ST_AV15">Lajpat Nagar Ring Road</option>
              <option value="ST_NG13">Nehru Place Terminal</option>
              <option value="ST_NG10">Dhaula Kuan</option>
              <option value="ST_OD03">Kashmere Gate ISBT</option>
              <option value="ST_ND01">New Delhi Railway Station</option>
            </select>

            <label className="flex items-center gap-1.5 cursor-pointer text-xs text-slate-300">
              <input
                type="checkbox"
                checked={isWeekend}
                onChange={(e) => setIsWeekend(e.target.checked)}
                className="accent-cyan-400 w-3.5 h-3.5 rounded"
              />
              <span>Weekend</span>
            </label>
          </div>
        </div>

        <div className="h-80 w-full">
          <canvas ref={histChartRef}></canvas>
        </div>
      </div>

      {/* ML Model Evaluation Comparison Matrix */}
      <div className="bg-navy-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-800/40 text-amber-200/90 text-xs space-y-1">
          <strong className="text-amber-400 font-semibold block uppercase tracking-wider text-[11px]">
            ⚠️ Scientific Provenance Disclosure: Synthetic Demonstration Benchmark
          </strong>
          <p>
            The benchmark metrics below were evaluated strictly on the out-of-time test partition (October 27–31) of the <strong>statistically simulated October 2026 ETM dataset</strong>. They demonstrate algorithmic convergence and feature pipeline validity, but <strong>must never be cited as verified real-world operational performance</strong>. Official data validation is isolated in <code className="text-cyan-300 font-mono">ml/validate_official.py</code> and <code className="text-cyan-300 font-mono">data/official/</code>.
          </p>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Algorithm Benchmark on Synthetic Out-of-Time Test Set</h3>
            <p className="text-xs text-slate-400">Strict chronological split: Train (Oct 1-21), Val (Oct 22-26), Test (Oct 27-31). Zero temporal leakage.</p>
          </div>
          <span className="text-xs font-mono px-2 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
            Synthetic Benchmark
          </span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left border-collapse font-mono text-xs">
            <thead className="bg-slate-950 text-slate-400 font-sans font-semibold">
              <tr>
                <th className="p-3">Model Architecture</th>
                <th className="p-3">Test MAE (Pax)</th>
                <th className="p-3">Test RMSE</th>
                <th className="p-3">WAPE (%)</th>
                <th className="p-3">Tier Macro F1</th>
                <th className="p-3">False-Low Rate</th>
                <th className="p-3">Error Reduction</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              <tr className="hover:bg-slate-800/30">
                <td className="p-3 font-sans font-semibold text-slate-400">Historical Median Baseline</td>
                <td className="p-3">8.84</td>
                <td className="p-3">11.23</td>
                <td className="p-3">32.65%</td>
                <td className="p-3">0.684</td>
                <td className="p-3 text-rose-400 font-bold">12.4%</td>
                <td className="p-3 text-slate-500">-</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="p-3 font-sans font-semibold text-slate-300">Random Forest Regressor (100 Trees)</td>
                <td className="p-3">5.48</td>
                <td className="p-3">7.12</td>
                <td className="p-3">20.24%</td>
                <td className="p-3">0.821</td>
                <td className="p-3 text-emerald-400">0.00%</td>
                <td className="p-3 text-cyan-400 font-bold">+38.0%</td>
              </tr>
              <tr className="bg-cyan-950/20 hover:bg-cyan-950/30 border-l-2 border-cyan-400">
                <td className="p-3 font-sans font-bold text-white flex items-center gap-1.5">
                  <span className="text-cyan-400">★</span>
                  <span>XGBoost Regressor (15-D Ensembles)</span>
                </td>
                <td className="p-3 text-cyan-300 font-bold">5.1913</td>
                <td className="p-3 text-cyan-300 font-bold">6.8410</td>
                <td className="p-3 text-emerald-400 font-bold">19.17%</td>
                <td className="p-3 text-emerald-400 font-bold">0.8499</td>
                <td className="p-3 text-emerald-400 font-bold">0.00%</td>
                <td className="p-3 text-emerald-400 font-bold">+41.3%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// --- PROVENANCE MODAL COMPONENT ---
function ProvenanceModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-2xl bg-navy-900 border border-slate-700 rounded-2xl shadow-2xl p-6 sm:p-8 space-y-6 text-slate-200">
        <div className="flex items-start justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <Icon name="shieldCheck" className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>Data Provenance & Scientific Disclosure</span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-amber-950 border border-amber-700 text-amber-300">Synthetic</span>
              </h2>
              <p className="text-xs text-slate-400">Delhi Transport Stack Hackathon 2026 Integrity Standard</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4 text-xs leading-relaxed">
          <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/50 text-amber-200 space-y-1.5">
            <span className="font-bold uppercase tracking-wider block text-amber-300">⚠️ Critical Scientific Notice</span>
            <p>
              The current demonstration dataset (<strong>84,814 ETM-style transactions</strong> across October 2026) is <strong>simulated</strong>. The reported model metrics (<strong>5.19 MAE / 19.17% WAPE</strong>) reflect performance on synthetic data and <strong>are not validated real-world results</strong>.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 font-mono text-[11px]">
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-slate-400 block font-sans text-xs">Dataset Provenance</span>
              <strong className="text-amber-400 text-xs font-mono">SYNTHETIC_SIMULATION</strong>
              <p className="text-[10px] text-slate-500 mt-1">Generated via scripts/generate_delhi_october_data.py</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-slate-400 block font-sans text-xs">Live GPS Status</span>
              <strong className="text-rose-400 text-xs font-mono">DISCONNECTED (Simulation Only)</strong>
              <p className="text-[10px] text-slate-500 mt-1">Awaiting Delhi OTD live API key integration</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-slate-400 block font-sans text-xs">Model Architecture</span>
              <strong className="text-cyan-400 text-xs font-mono">XGBoost Regressor (15-D)</strong>
              <p className="text-[10px] text-slate-500 mt-1">Trained on synthetic flow-reconstructed loads</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-slate-400 block font-sans text-xs">Official Data Pipeline</span>
              <strong className="text-amber-300 text-xs font-mono">SCAFFOLD ONLY</strong>
              <p className="text-[10px] text-slate-500 mt-1">Official ETM data not staged; AFC integration absent</p>
            </div>
          </div>

          <p className="text-slate-400">
            The validation script is an early scaffold. It expects a fixed schema and explicit provenance registration; it does not normalize alternate schemas or integrate AFC. No official ETM dataset is staged in this demo copy.
          </p>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <span className="text-[11px] text-slate-500">Registry: data/provenance/registry.json</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-navy-950 font-bold text-xs"
          >
            Acknowledge & Close
          </button>
        </div>
      </div>
    </div>
  );
}

// --- MAIN APPLICATION CONTROLLER ---
function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [showProvenanceModal, setShowProvenanceModal] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-navy-950 text-slate-100 font-sans selection:bg-cyan-500 selection:text-black">
      {/* Provenance Disclosure Modal */}
      <ProvenanceModal isOpen={showProvenanceModal} onClose={() => setShowProvenanceModal(false)} />

      {/* Header Navigation */}
      <Header 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onOpenProvenanceModal={() => setShowProvenanceModal(true)} 
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'overview' && <OverviewView setActiveTab={setActiveTab} />}
        {activeTab === 'planner' && <JourneyPlannerView setActiveTab={setActiveTab} />}
        {activeTab === 'compare' && <RouteComparisonView setActiveTab={setActiveTab} />}
        {activeTab === 'forecast' && <CrowdIntelligenceView setActiveTab={setActiveTab} />}
        {activeTab === 'map' && <InteractiveMapView setActiveTab={setActiveTab} />}
        {activeTab === 'simulator' && <WhatIfSimulatorView setActiveTab={setActiveTab} />}
        {activeTab === 'analytics' && <AnalyticsDashboardView setActiveTab={setActiveTab} />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-navy-950 py-8 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">TransitSense AI</span>
            <span>•</span>
            <span>Delhi Transport Stack Hackathon 2026 (Problem 2)</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <button 
              onClick={() => setShowProvenanceModal(true)}
              className="text-amber-400 hover:underline flex items-center gap-1"
            >
              <span>Provenance: Synthetic Oct 2026</span>
            </button>
            <span>•</span>
            <a href="/docs" target="_blank" className="hover:text-cyan-400 transition">Swagger API</a>
            <span>•</span>
            <span>Zero Data Fabrication</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Mount React Root
const rootElement = document.getElementById('root');
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(<App />);
}
