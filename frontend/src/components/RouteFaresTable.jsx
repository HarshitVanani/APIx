import React from 'react';
import { Tag, CheckCircle2 } from 'lucide-react';

const LIVE_OBSERVATIONS = [
  { id: 'REC-101', route: 'DEL ➔ BOM', carrier: 'IndiGo', flightNo: '6E-2041', depTime: '06:15', window: 'T+1', base: 7350, tax: 1170, total: 8520, seats: 4 },
  { id: 'REC-102', route: 'DEL ➔ BOM', carrier: 'Air India', flightNo: 'AI-805', depTime: '07:30', window: 'T+1', base: 7680, tax: 1220, total: 8900, seats: 6 },
  { id: 'REC-103', route: 'DEL ➔ BOM', carrier: 'SpiceJet', flightNo: 'SG-105', depTime: '14:20', window: 'T+7', base: 5000, tax: 800, total: 5800, seats: 5 },
  { id: 'REC-104', route: 'DEL ➔ BOM', carrier: 'Akasa Air', flightNo: 'QP-1102', depTime: '18:45', window: 'T+15', base: 4140, tax: 660, total: 4800, seats: 9 },
  { id: 'REC-105', route: 'BLR ➔ DEL', carrier: 'IndiGo', flightNo: '6E-2217', depTime: '09:10', window: 'T+15', base: 5080, tax: 820, total: 5900, seats: 7 },
  { id: 'REC-106', route: 'BLR ➔ DEL', carrier: 'Air India', flightNo: 'AI-503', depTime: '11:45', window: 'T+30', base: 4740, tax: 760, total: 5500, seats: 8 },
  { id: 'REC-107', route: 'DEL ➔ CCU', carrier: 'Akasa Air', flightNo: 'QP-1405', depTime: '16:00', window: 'T+45', base: 3450, tax: 550, total: 4000, seats: 9 },
];

export default function RouteFaresTable() {
  return (
    <div className="mt-6 p-6 bg-slate-900/80 border border-slate-800 rounded-2xl">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <Tag className="w-4 h-4 text-blue-400" />
            Live Cleaned Fare Observations (Motor Database Sync)
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time extracted fares post deduplication and IQR outlier filtration
          </p>
        </div>
        <span className="text-xs px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-lg flex items-center gap-1.5 font-medium">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Cleaned Schema (161 Records)
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
              <th className="pb-3 px-3">Flight Ref</th>
              <th className="pb-3 px-3">Route</th>
              <th className="pb-3 px-3">Carrier</th>
              <th className="pb-3 px-3">Schedule</th>
              <th className="pb-3 px-3">Window</th>
              <th className="pb-3 px-3 text-right">Base Fare</th>
              <th className="pb-3 px-3 text-right">Taxes & Fees</th>
              <th className="pb-3 px-3 text-right">Total Price</th>
              <th className="pb-3 px-3 text-center">Availability</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {LIVE_OBSERVATIONS.map((row) => (
              <tr key={row.id} className="hover:bg-slate-800/40 transition">
                <td className="py-3 px-3 text-slate-400">{row.id}</td>
                <td className="py-3 px-3 font-sans font-semibold text-white">{row.route}</td>
                <td className="py-3 px-3 font-sans">
                  <span
                    className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                      row.carrier === 'IndiGo'
                        ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                        : row.carrier === 'Air India'
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                        : row.carrier === 'SpiceJet'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}
                  >
                    {row.carrier} ({row.flightNo})
                  </span>
                </td>
                <td className="py-3 px-3 text-slate-400">{row.depTime}</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded border border-slate-700">
                    {row.window}
                  </span>
                </td>
                <td className="py-3 px-3 text-right text-slate-400">₹{row.base.toLocaleString('en-IN')}</td>
                <td className="py-3 px-3 text-right text-slate-500">₹{row.tax.toLocaleString('en-IN')}</td>
                <td className="py-3 px-3 text-right font-bold text-white">₹{row.total.toLocaleString('en-IN')}</td>
                <td className="py-3 px-3 text-center">
                  <span className="text-emerald-400 font-semibold">{row.seats} Left</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}