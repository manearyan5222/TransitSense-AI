import React, { useState } from 'react';

export function App() {
  const [activeTab, setActiveTab] = useState('planner');

  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100 flex flex-col font-sans">
      <header className="sticky top-0 z-50 bg-[#090D16]/90 backdrop-blur border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center font-bold text-white shadow-lg">
              TS
            </div>
            <div>
              <span className="font-extrabold text-lg text-white">TransitSense <span className="text-cyan-400">AI</span></span>
              <p className="text-[11px] text-slate-400">Delhi Transport Stack 2026</p>
            </div>
          </div>

          <nav className="flex items-center gap-2">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'planner', label: 'Journey Planner' },
              { id: 'compare', label: 'Route Comparison' },
              { id: 'forecast', label: 'Crowd Intelligence' },
              { id: 'map', label: 'Network Map' },
              { id: 'simulator', label: 'Simulator' },
              { id: 'analytics', label: 'Analytics' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  activeTab === tab.id 
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' 
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        <div className="p-8 rounded-2xl bg-[#0F172A] border border-slate-800 text-center space-y-4">
          <h2 className="text-2xl font-bold text-white">TransitSense AI Frontend Service</h2>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            The full-featured interactive single-page application is served natively through the FastAPI backend at <code className="text-cyan-400 font-mono">http://localhost:8000/</code> or <code className="text-cyan-400 font-mono">/app</code> with zero setup required.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
