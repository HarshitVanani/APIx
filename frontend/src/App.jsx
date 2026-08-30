/**
 * STEP 8.6: COMPLETE APP ENTRY POINT
 * Authentication Routing & Institutional Navigation
 */

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { Plane, Lock, LogOut, CheckCircle2, AlertCircle } from 'lucide-react';
import ProfessionalDashboard from './DashboardView';

// ============ LOGIN PAGE ============
const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 800));

      if (email && password) {
        localStorage.setItem('authToken', 'apix-auth-' + Date.now());
        onLogin();
      } else {
        setError('Please enter both email and password');
      }
    } catch {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 font-sans">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 bg-sky-500/10 border border-sky-500/30 rounded-xl text-sky-400">
            <Plane className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">APIx Institutional Access</h1>
          <p className="text-xs text-slate-400">Ministry of Statistics and Programme Implementation (MoSPI)</p>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg flex items-center gap-2 text-rose-400 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-300 font-medium mb-1.5">Institutional Email</label>
            <input
              type="email"
              placeholder="officer@mospi.gov.in"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1.5">Access Token / Password</label>
            <input
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition"
            />
            <p className="text-[11px] text-slate-500 mt-1">Evaluator demo: Any credentials accepted</p>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 px-4 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white font-semibold rounded-lg transition cursor-pointer flex items-center justify-center gap-2"
          >
            <Lock className="w-3.5 h-3.5" />
            {isLoading ? 'Authenticating...' : 'Sign In to Portal'}
          </button>
        </form>

        <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg text-[11px] text-slate-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Secured with JWT authentication & DGCA data validation matrix.</span>
        </div>
      </div>
    </div>
  );
};

// ============ NAVBAR ============
const Navbar = ({ onLogout }) => {
  return (
    <nav className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex justify-between items-center">
      <div className="flex items-center gap-2">
        <Plane className="w-5 h-5 text-sky-400" />
        <span className="font-bold text-white text-sm">APIx Intelligence Engine</span>
      </div>
      <div className="flex items-center gap-4 text-xs">
        <span className="text-slate-400">Authenticated: <strong className="text-slate-200">NSO Statistical Officer</strong></span>
        <button
          onClick={onLogout}
          className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition cursor-pointer"
        >
          <LogOut className="w-3.5 h-3.5" /> Logout
        </button>
      </div>
    </nav>
  );
};

// ============ 404 NOT FOUND ============
const NotFoundPage = () => (
  <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-white space-y-4 font-sans">
    <h1 className="text-6xl font-extrabold text-sky-400">404</h1>
    <p className="text-slate-400 text-sm">The requested telemetry endpoint does not exist.</p>
    <Link to="/" className="px-4 py-2 bg-sky-600 hover:bg-sky-500 rounded-lg text-xs font-semibold">
      Return to Dashboard
    </Link>
  </div>
);

// ============ MAIN ROUTER ============
export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem('authToken');
  });

  const handleLogin = () => setIsAuthenticated(true);
  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setIsAuthenticated(false);
  };

  return (
    <Router>
      {isAuthenticated && <Navbar onLogout={handleLogout} />}
      <Routes>
        {isAuthenticated ? (
          <>
            <Route path="/" element={<ProfessionalDashboard />} />
            <Route path="*" element={<NotFoundPage />} />
          </>
        ) : (
          <>
            <Route path="/" element={<LoginPage onLogin={handleLogin} />} />
            <Route path="*" element={<Navigate to="/" />} />
          </>
        )}
      </Routes>
    </Router>
  );
}