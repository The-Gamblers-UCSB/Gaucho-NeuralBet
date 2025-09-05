import React, { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

/* ------------------------------------------------------------------
   Gaucho NeuralBet – Dashboard v2  
   – Radial-gradient canvas + animated floating blobs
   – Full-width hero banner, sticky glass card centred on page
   – Framer-motion hover & tap effects for tactile UI
   – Accessible focus rings + prefers-color-scheme support
   ------------------------------------------------------------------ */

const STATS = [
  { value: "PTS", label: "Points", icon: "🏀" },
  { value: "REB", label: "Rebounds", icon: "📊" },
  { value: "AST", label: "Assists", icon: "🤝" },
  { value: "STL", label: "Steals", icon: "✋" },
  { value: "BLK", label: "Blocks", icon: "🚫" },
  { value: "FG3M", label: "3-Pt FG", icon: "🎯" },
  { value: "FTM", label: "Free Throws", icon: "🎳" },
];

const POPULARS = [
  { name: "LeBron James", team: "LAL" },
  { name: "Stephen Curry", team: "GSW" },
  { name: "Giannis Antetokounmpo", team: "MIL" },
  { name: "Luka Doncic", team: "DAL" },
  { name: "Jayson Tatum", team: "BOS" },
  { name: "Nikola Jokic", team: "DEN" },
  { name: "Joel Embiid", team: "PHI" },
  { name: "Damian Lillard", team: "MIL" },
];

export default function Dashboard() {
  const [player, setPlayer] = useState("");
  const [stat, setStat] = useState("PTS");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const handlePredict = async () => {
    if (!player.trim()) return setErr("Enter a player name first.");
    setBusy(true); setErr(""), setResult(null);
    try {
      const { data } = await axios.post("http://localhost:5001/api/nba/predict", {
        playerName: player.trim(), stat,
      });
      if (!data?.success) throw new Error(data?.error || "Unknown error");
      setResult(data);
    } catch (e) {
      setErr(e.message);
    } finally { setBusy(false); }
  };

  const statInfo = STATS.find(s => s.value === stat);

  return (
    <main className="relative min-h-screen font-sans text-slate-200 bg-[radial-gradient(circle_at_20%_20%,#152036_0%,#0b1120_70%)] overflow-x-hidden">
      <Blobs />

      {/* HERO */}
      <header className="pt-20 md:pt-28 text-center space-y-4">
        <motion.div whileHover={{ rotate: 25 }} className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-orange-500 to-red-600 shadow-lg shadow-red-600/30">
          <span className="text-4xl">🏀</span>
        </motion.div>
        <h1 className="text-4xl md:text-5xl font-extrabold bg-gradient-to-r from-amber-200 via-orange-300 to-pink-300 bg-clip-text text-transparent select-none">
          NBA Prediction AI
        </h1>
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto">
          Game-by-game performance forecasts powered by machine learning.
        </p>
      </header>

      {/* CARD */}
      <section className="relative z-10 mx-auto mt-12 w-full max-w-5xl px-4">
        <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-3xl shadow-2xl ring-1 ring-white/10 overflow-hidden">
          <div className="grid md:grid-cols-2 gap-8 p-8 md:p-12">
            {/* LEFT – INPUTS */}
            <div className="space-y-8">
              <div>
                <h3 className="text-slate-300 font-semibold mb-3">Popular players</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {POPULARS.map(p => (
                    <motion.button
                      whileTap={{ scale: 0.9 }}
                      key={p.name}
                      onClick={() => setPlayer(p.name)}
                      className="rounded-xl bg-white/10 px-4 py-3 border border-transparent hover:border-blue-500/60 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-600/40">
                      <p className="text-sm font-medium truncate">{p.name}</p>
                      <p className="text-xs text-slate-400">{p.team}</p>
                    </motion.button>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <InputBlock label="Player name">
                  <input
                    value={player}
                    onChange={e => setPlayer(e.target.value)}
                    placeholder="e.g. LeBron James"
                    className="w-full bg-transparent placeholder-slate-500 rounded-xl border border-white/10 px-5 py-4 focus:outline-none focus:ring-2 focus:ring-blue-600/40" />
                </InputBlock>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <InputBlock label="Statistic">
                    <select
                      value={stat}
                      onChange={e => setStat(e.target.value)}
                      className="w-full bg-transparent rounded-xl border border-white/10 px-5 py-4 focus:outline-none focus:ring-2 focus:ring-blue-600/40">
                      {STATS.map(s => <option key={s.value} value={s.value} className="bg-slate-800">{s.icon} {s.label}</option>)}
                    </select>
                  </InputBlock>
                  <div className="flex items-end">
                    <motion.button
                      whileTap={{ scale: 0.95 }}
                      onClick={handlePredict}
                      disabled={busy || !player.trim()}
                      className="w-full flex justify-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-700 hover:to-purple-800 rounded-xl py-4 font-semibold disabled:opacity-40 disabled:cursor-not-allowed shadow-lg focus:outline-none focus:ring-2 focus:ring-indigo-400/60">
                      {busy ? (<Spinner />) : '🎯 Get Prediction'}
                    </motion.button>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT – OUTPUT */}
            <div className="flex items-center justify-center min-h-[14rem]">
              {busy && <Loading />}
              {!busy && err && <Message type="error" msg={err} />}
              {!busy && !err && result && <ResultDisplay data={result} info={statInfo} />}
              {!busy && !err && !result && <Message type="idle" />}
            </div>
          </div>
        </div>
      </section>

      <footer className="py-10 text-center text-xs text-slate-500">
        ⚡ Gaucho NeuralBet • React + Tailwind CSS + Framer-Motion
      </footer>
    </main>
  );
}

// COMPONENTS ------------------------------
const InputBlock = ({ label, children }) => (
  <label className="flex flex-col gap-2 text-sm font-medium text-slate-300">{label}{children}</label>
);

const Spinner = () => (
  <div className="h-5 w-5 border-2 border-transparent border-t-white rounded-full animate-spin" />
);

const Loading = () => (
  <div className="flex flex-col items-center gap-2 text-slate-300"><Spinner /><span>Crunching numbers…</span></div>
);

const Message = ({ type = 'idle', msg }) => {
  if (type === 'idle') return <p className="text-slate-400 text-center">Enter a player & stat to begin.</p>;
  return (
    <div className="bg-red-500/10 border border-red-600/30 rounded-xl px-6 py-4 text-center text-red-300 max-w-sm">❌ {msg}</div>
  );
};

const ResultDisplay = ({ data, info }) => (
  <div className="w-full space-y-6">
    <h2 className="text-center text-2xl font-bold mb-2">{info.icon} {info.label} – {data.player}</h2>
    <div className="flex gap-4 overflow-x-auto no-scrollbar snap-x snap-mandatory px-1">
      <StatCard className="min-w-[240px] snap-start" gradient="from-blue-600 to-blue-500" title={`Predicted ${info.label}`} value={data.prediction} />
      <StatCard className="min-w-[240px] snap-start" gradient="from-emerald-600 to-emerald-500" title="Confidence" value={`${data.confidence}%`} />
      <StatCard className="min-w-[240px] snap-start" gradient="from-purple-600 to-purple-500" title="Range" value={`${data.range.min}–${data.range.max}`} />
    </div>
    <div className="flex flex-wrap items-center justify-center gap-3 text-sm text-slate-300 max-w-2xl mx-auto">
      <MetaChip k="Games analysed" v={data.data_points} />
      <MetaChip k="Model MAE" v={data.mae} />
    </div>
  </div>
);

const StatCard = ({ title, value, gradient, className = "" }) => (
  <div className={`text-center rounded-2xl p-5 bg-gradient-to-br ${gradient} shadow-lg ${className}`}>
    <p className="text-4xl font-bold mb-1">{value}</p>
    <p className="text-xs tracking-wide opacity-80">{title}</p>
  </div>
);

const MetaChip = ({ k, v }) => (
  <div className="px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm">
    <span className="opacity-70 mr-1">{k}:</span>
    <span className="font-semibold text-slate-100">{v}</span>
  </div>
);

const Blobs = () => (
  <div className="pointer-events-none absolute inset-0 overflow-hidden">
    <div className="absolute -top-32 -left-32 w-[32rem] h-[32rem] bg-pink-500 opacity-20 blur-3xl rounded-full animate-blob" />
    <div className="absolute top-1/2 -right-32 w-[32rem] h-[32rem] bg-cyan-500 opacity-20 blur-3xl rounded-full animate-blob animation-delay-2000" />
    <div className="absolute bottom-0 left-1/3 w-[32rem] h-[32rem] bg-violet-600 opacity-20 blur-3xl rounded-full animate-blob animation-delay-4000" />
  </div>
);
