import React, { useState } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import { PlaneTakeoff, ShieldCheck, ArrowRightLeft, Layers } from 'lucide-react';

const SAMPLE_ROUTES = [
  {
    route: 'DEL ➔ BOM',
    distance: '1,148 km',
    currentAvg: 5420,
    dgcaBenchmark: 5100,
    variance: '+6.27%',
    carriers: ['IndiGo', 'Air India', 'SpiceJet', 'Akasa Air'],
    elasticity: [
      { window: 'T+1', IndiGo: 8520, AirIndia: 8900, SpiceJet: 7900, Akasa: 7600 },
      { window: 'T+7', IndiGo: 6100, AirIndia: 6400, SpiceJet: 5800, Akasa: 5600 },
      { window: 'T+15', IndiGo: 5200, AirIndia: 5600, SpiceJet: 4900, Akasa: 4800 },
      { window: 'T+30', IndiGo: 4600, AirIndia: 5100, SpiceJet: 4400, Akasa: 4200 },
      { window: 'T+45', IndiGo: 4200, AirIndia: 4800, SpiceJet: 4100, Akasa: 3950 },
    ],
  },
  {
    route: 'BLR ➔ DEL',
    distance: '1,740 km',
    currentAvg: 5890,
    dgcaBenchmark: 5750,
    variance: '+2.43%',
    carriers: ['IndiGo', 'Air India', 'Akasa Air'],
    elasticity: [
      { window: 'T+1', IndiGo: 9100, AirIndia: 9600, SpiceJet: 8700, Akasa: 8400 },
      { window: 'T+7', IndiGo: 6800, AirIndia: 7200, SpiceJet: 6400, Akasa: 6200 },
      { window: 'T+15', IndiGo: 5900, AirIndia: 6300, SpiceJet: 5600, Akasa: 5500 },
      { window: 'T+30', IndiGo: 5100, AirIndia: 5500, SpiceJet: 4900, Akasa: 4800 },
      { window: 'T+45', IndiGo: 4700, AirIndia: 5100, SpiceJet: 4500, Akasa: 4400 },
    ],
  },
  {
    route: 'DEL ➔ CCU',
    distance: '1,305 km',
    currentAvg: 5310,
    dgcaBenchmark: 5400,
    variance: '-1.67%',
    carriers: ['IndiGo', 'Air India', 'SpiceJet'],
    elasticity: [
      { window: 'T+1', IndiGo: 8200, AirIndia: 8600, SpiceJet: 7800, Akasa: 7500 },
      { window: 'T+7', IndiGo: 6000, AirIndia: 6300, SpiceJet: 5700, Akasa: 5500 },
      { window: 'T+15', IndiGo: 5300, AirIndia: 5700, SpiceJet: 5000, Akasa: 4900 },
      { window: 'T+30', IndiGo: 4700, AirIndia: 5100, SpiceJet: 4500, Akasa: 4300 },
      { window: 'T+45', IndiGo: 4300, AirIndia: 4700, SpiceJet: 4100, Akasa: 4000 },
    ],
  },
];

export default function RouteAnalytics() {
  const [selectedRouteIndex, setSelectedRouteIndex] = useState(0);
  const activeRoute = SAMPLE_ROUTES[selectedRouteIndex];

  return (
    <div className="space-y-6 mt-6">
      {/* Route Selector Ribbon */}
      <div className="flex flex-wrap gap-3">
        {SAMPLE_ROUTES.map((item, idx) => (
          <button
            key={item.route}
            onClick={() => setSelectedRouteIndex(idx)}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl border text-sm font-medium transition ${
              selectedRouteIndex === idx
                ? 'bg-blue-600/15 border-blue-500/50 text-blue-400 shadow-md shadow-blue-500/10'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
            }`}
          >
            <PlaneTakeoff className="w-4 h-4" />
            <span>{item.route}</span>
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-mono font-semibold ${
                item.variance.startsWith('+')
                  ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              }`}
            >
              {item.variance}
            </span>
          </button>
        ))}
      </div>

      {/* Elasticity Chart & Metric Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Advance Window Elasticity Chart */}
        <div className="lg:col-span-2 p-6 bg-slate-900/80 border border-slate-800 rounded-2xl">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-blue-400" />
                Advance Purchase Window Price Elasticity (₹)
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Dynamic carrier fare surge from T+45 (Early Bird) to T+1 (Last-Minute Booking)
              </p>
            </div>
            <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md border border-slate-700">
              {activeRoute.distance}
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={activeRoute.elasticity} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="window" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
                <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#94a3b8' }}
                  formatter={(val, name) => [`₹${val}`, name]}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="IndiGo" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="AirIndia" fill="#ef4444" radius={[4, 4, 0, 0]} />
                <Bar dataKey="SpiceJet" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Akasa" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* DGCA Compliance & Regulatory Variance */}
        <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-2xl flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-slate-200 font-semibold mb-4">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span>DGCA Benchmark Calibration</span>
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl">
                <span className="text-xs text-slate-400 block">Current Market Weighted Average</span>
                <span className="text-2xl font-bold text-white mt-1 block">
                  ₹{activeRoute.currentAvg.toLocaleString('en-IN')}
                </span>
              </div>

              <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl">
                <span className="text-xs text-slate-400 block">DGCA Statutory Baseline Reference</span>
                <span className="text-2xl font-bold text-slate-300 mt-1 block">
                  ₹{activeRoute.dgcaBenchmark.toLocaleString('en-IN')}
                </span>
              </div>

              <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl flex justify-between items-center">
                <div>
                  <span className="text-xs text-slate-400 block">Surge Pricing Delta</span>
                  <span className="text-xs text-slate-500">Allowed Corridor: ±15%</span>
                </div>
                <span
                  className={`text-base font-bold font-mono ${
                    activeRoute.variance.startsWith('+') ? 'text-amber-400' : 'text-emerald-400'
                  }`}
                >
                  {activeRoute.variance}
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-800 text-xs text-slate-500 flex items-center justify-between">
            <span>Status: Statutory Compliant</span>
            <span className="text-emerald-400 font-medium">Within Limits</span>
          </div>
        </div>
      </div>
    </div>
  );
}