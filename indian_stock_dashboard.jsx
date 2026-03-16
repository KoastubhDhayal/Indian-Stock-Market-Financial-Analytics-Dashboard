import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { TrendingUp, TrendingDown, AlertCircle, DollarSign, Activity, Bell, LayoutDashboard, Search, ChevronRight } from 'lucide-react';

// --- Logic remains identical to your original code ---
const fetchStockData = async (symbol) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const basePrice = Math.random() * 1000 + 500;
      const change = (Math.random() - 0.5) * 50;
      resolve({
        symbol,
        price: basePrice,
        change: change,
        changePercent: (change / basePrice) * 100,
        volume: Math.floor(Math.random() * 10000000),
        high: basePrice + Math.random() * 20,
        low: basePrice - Math.random() * 20,
        open: basePrice - Math.random() * 10,
      });
    }, 100);
  });
};

const predictStockPrice = (historicalData) => {
  if (!historicalData || historicalData.length === 0) return null;
  const recent = historicalData.slice(-5);
  const avg = recent.reduce((sum, d) => sum + d.price, 0) / recent.length;
  const trend = recent[recent.length - 1].price - recent[0].price;
  return {
    predicted: avg + (trend * 0.3),
    confidence: Math.random() * 0.3 + 0.65,
    horizon: '1 day',
    signal: trend > 0 ? 'bullish' : 'bearish'
  };
};

const generateRecommendation = (stockData, prediction, riskProfile = 'moderate') => {
  const { changePercent, volume, price } = stockData;
  const { predicted, confidence, signal } = prediction;
  let recommendation = 'HOLD';
  let reasoning = [];
  if (signal === 'bullish' && confidence > 0.7 && changePercent > 0) {
    recommendation = 'BUY';
    reasoning.push('Strong bullish signal with high confidence');
    reasoning.push(`Predicted upside: ${((predicted - price) / price * 100).toFixed(2)}%`);
  } else if (signal === 'bearish' && confidence > 0.7 && changePercent < -2) {
    recommendation = 'SELL';
    reasoning.push('Bearish trend with downside risk');
  } else if (Math.abs(changePercent) < 1 && confidence < 0.7) {
    recommendation = 'HOLD';
    reasoning.push('Market uncertainty - await clearer signals');
  }
  if (volume > 5000000) reasoning.push('High trading volume indicates strong interest');
  return { action: recommendation, reasoning, targetPrice: predicted, stopLoss: price * 0.95, riskLevel: confidence < 0.6 ? 'High' : confidence > 0.75 ? 'Low' : 'Medium' };
};

const StockDashboard = () => {
  const [selectedStock, setSelectedStock] = useState('RELIANCE');
  const [stockData, setStockData] = useState({});
  const [historicalData, setHistoricalData] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [watchlist, setWatchlist] = useState(['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']);
  const [portfolioValue] = useState(1524850.42);

  const popularStocks = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 
    'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
    'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'TITAN'
  ];

  const generateHistoricalData = (days = 30) => {
    const data = [];
    let price = Math.random() * 1000 + 500;
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      price += (Math.random() - 0.48) * 20;
      data.push({
        date: date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }),
        price: parseFloat(price.toFixed(2)),
      });
    }
    return data;
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const data = await fetchStockData(selectedStock);
      setStockData(data);
      const historical = generateHistoricalData(30);
      setHistoricalData(historical);
      const pred = predictStockPrice(historical);
      setPrediction(pred);
      setRecommendation(generateRecommendation(data, pred));
      setLoading(false);
    };
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [selectedStock]);

  const calculateRSI = (data, period = 14) => {
    if (data.length < period) return 50;
    const changes = data.slice(-period).map((d, i, arr) => i === 0 ? 0 : d.price - arr[i - 1].price);
    const gains = changes.filter(c => c > 0).reduce((sum, c) => sum + c, 0) / period;
    const losses = Math.abs(changes.filter(c => c < 0).reduce((sum, c) => sum + c, 0)) / period;
    return losses === 0 ? 100 : 100 - (100 / (1 + (gains / losses)));
  };

  const rsi = calculateRSI(historicalData);

  // Style helpers
  const getRecStyles = (action) => {
    switch(action) {
      case 'BUY': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/50';
      case 'SELL': return 'bg-rose-500/10 text-rose-400 border-rose-500/50';
      default: return 'bg-amber-500/10 text-amber-400 border-amber-500/50';
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans selection:bg-blue-500/30">
      {/* Top Navigation Bar */}
      <nav className="border-b border-white/5 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-[1600px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Activity size={20} className="text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white">
              Market<span className="text-blue-500">Mind</span>
            </h1>
          </div>
          
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <span className="text-blue-400 cursor-pointer">Dashboard</span>
            <span className="hover:text-white cursor-pointer transition-colors">Portfolio</span>
            <span className="hover:text-white cursor-pointer transition-colors">Markets</span>
          </div>

          <div className="flex items-center gap-6">
             <div className="text-right hidden sm:block">
                <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Total Portfolio</p>
                <p className="text-lg font-mono font-bold text-emerald-400">₹{portfolioValue.toLocaleString('en-IN')}</p>
             </div>
             <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 border border-white/10" />
          </div>
        </div>
      </nav>

      <main className="max-w-[1600px] mx-auto p-6 space-y-6">
        
        {/* Search & Select Row */}
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-slate-800/30 p-4 rounded-2xl border border-white/5 shadow-2xl">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <select 
              value={selectedStock}
              onChange={(e) => setSelectedStock(e.target.value)}
              className="w-full bg-slate-900/50 text-white pl-10 pr-4 py-2.5 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none appearance-none cursor-pointer transition-all"
            >
              {popularStocks.map(stock => <option key={stock} value={stock}>{stock}</option>)}
            </select>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">NSE Live</span>
            </div>
            <button className="p-2.5 rounded-xl bg-slate-800 border border-white/5 hover:bg-slate-700 transition-colors">
              <Bell size={18} />
            </button>
          </div>
        </div>

        {/* Hero Section */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Main Chart Area */}
          <div className="lg:col-span-3 space-y-6">
            <div className="bg-slate-800/40 backdrop-blur-md rounded-3xl p-8 border border-white/5 shadow-xl">
              <div className="flex flex-wrap justify-between items-end mb-8 gap-4">
                <div>
                  <h2 className="text-slate-400 text-sm font-semibold uppercase tracking-widest mb-1">{selectedStock} / INR</h2>
                  <div className="flex items-baseline gap-4">
                    <span className="text-5xl font-bold text-white tracking-tighter">₹{stockData.price?.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
                    <div className={`flex items-center font-bold px-2 py-1 rounded-lg text-sm ${stockData.change >= 0 ? 'text-emerald-400 bg-emerald-400/10' : 'text-rose-400 bg-rose-400/10'}`}>
                      {stockData.change >= 0 ? <TrendingUp size={16} className="mr-1"/> : <TrendingDown size={16} className="mr-1"/>}
                      {Math.abs(stockData.changePercent)?.toFixed(2)}%
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-8 text-right">
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase mb-1">24h High</p>
                    <p className="text-lg font-mono font-semibold text-slate-200">₹{stockData.high?.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase mb-1">24h Low</p>
                    <p className="text-lg font-mono font-semibold text-slate-200">₹{stockData.low?.toFixed(2)}</p>
                  </div>
                </div>
              </div>

              <div className="h-[400px] w-full mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={historicalData}>
                    <defs>
                      <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                    <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={['auto', 'auto']} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #ffffff10', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.5)' }}
                      itemStyle={{ color: '#3b82f6', fontWeight: 'bold' }}
                    />
                    <Area type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={3} fill="url(#chartGradient)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Quick Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Volume', val: `${(stockData.volume / 1000000).toFixed(2)}M`, color: 'text-white' },
                { label: 'RSI (14)', val: rsi.toFixed(2), color: rsi > 70 ? 'text-rose-400' : rsi < 30 ? 'text-emerald-400' : 'text-blue-400' },
                { label: 'AI Confidence', val: `${(prediction?.confidence * 100).toFixed(1)}%`, color: 'text-purple-400' },
                { label: 'Trend Signal', val: prediction?.signal?.toUpperCase(), color: prediction?.signal === 'bullish' ? 'text-emerald-400' : 'text-rose-400' },
              ].map((m, i) => (
                <div key={i} className="bg-slate-800/20 border border-white/5 p-5 rounded-2xl hover:bg-slate-800/40 transition-colors">
                  <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-2">{m.label}</p>
                  <p className={`text-xl font-mono font-bold ${m.color}`}>{m.val}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar Area */}
          <div className="space-y-6">
            {/* AI Action Card */}
            <div className="bg-gradient-to-b from-slate-800 to-slate-900 rounded-3xl p-6 border border-white/10 shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                <AlertCircle size={80} />
              </div>
              
              <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                AI Strategy
              </h3>
              
              {recommendation && (
                <div className="space-y-6">
                  <div className={`py-4 rounded-2xl border text-center text-3xl font-black tracking-widest ${getRecStyles(recommendation.action)}`}>
                    {recommendation.action}
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex justify-between items-center bg-white/5 p-3 rounded-xl">
                      <span className="text-sm text-slate-400">Target</span>
                      <span className="text-emerald-400 font-mono font-bold">₹{recommendation.targetPrice?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center bg-white/5 p-3 rounded-xl">
                      <span className="text-sm text-slate-400">Stop Loss</span>
                      <span className="text-rose-400 font-mono font-bold">₹{recommendation.stopLoss?.toFixed(2)}</span>
                    </div>
                  </div>

                  <div className="pt-4">
                    <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Logic Insights</p>
                    <ul className="space-y-3">
                      {recommendation.reasoning.map((reason, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2 leading-relaxed">
                          <ChevronRight size={14} className="text-blue-500 shrink-0 mt-0.5" />
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>

            {/* Watchlist Section */}
            <div className="bg-slate-900/40 rounded-3xl p-6 border border-white/5">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Quick Watch</h3>
              <div className="space-y-2">
                {watchlist.map(stock => (
                  <button
                    key={stock}
                    onClick={() => setSelectedStock(stock)}
                    className={`w-full flex justify-between items-center p-3 rounded-xl transition-all duration-200 border ${
                      selectedStock === stock 
                        ? 'bg-blue-600 border-blue-400 shadow-lg shadow-blue-900/20' 
                        : 'bg-slate-800/40 border-transparent hover:border-white/10'
                    }`}
                  >
                    <span className={`font-bold ${selectedStock === stock ? 'text-white' : 'text-slate-300'}`}>{stock}</span>
                    <span className="text-[10px] px-2 py-1 bg-black/20 rounded-md font-bold opacity-60">NSE</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

        </div>

        {/* Legal/Disclaimer */}
        <footer className="text-center py-10">
          <p className="text-slate-600 text-[11px] max-w-2xl mx-auto leading-relaxed uppercase tracking-tighter italic">
            Disclaimer: AI predictions are based on historical simulations and momentum algorithms. 
            Financial markets involve high risk. This dashboard is for educational visualization only.
          </p>
        </footer>
      </main>
    </div>
  );
};

export default StockDashboard;