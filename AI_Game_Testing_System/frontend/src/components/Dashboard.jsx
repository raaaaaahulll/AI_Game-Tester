import React, { useState, useEffect } from 'react';
import { startTest, stopTest, getMetrics, resetStatus, focusWindow } from '../services/api';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertOctagon, Layers, Cpu, Film, RefreshCw, LogOut } from 'lucide-react';
import { motion } from 'framer-motion';
import HeroControlPanel from './HeroControlPanel';

const MetricCard = ({ title, value, icon: Icon, color, subValue }) => (
    <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 relative group overflow-hidden"
    >
        {/* Hover highlight effect */}
        <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        <div className="relative z-10">
            <div className="flex justify-between items-start mb-4">
                <h3 className="text-[#a3a3a3] font-medium text-sm tracking-wider uppercase">{title}</h3>
                <Icon size={20} className={color === 'red' ? 'text-[#E50914]' : 'text-white/50'} />
            </div>

            <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold text-white tracking-tight">{value}</span>
            </div>
            {subValue && <span className="text-xs text-[#565656] font-mono mt-1 block">{subValue}</span>}
        </div>
    </motion.div>
);

const Dashboard = ({ onLogout }) => {
    const [status, setStatus] = useState("Idle");
    const [genre, setGenre] = useState("platformer");
    const [selectedWindow, setSelectedWindow] = useState(null);
    const [errorMessage, setErrorMessage] = useState("");
    const [metrics, setMetrics] = useState({
        coverage: 0,
        crashes: 0,
        current_algorithm: "None",
        total_steps: 0,
        window_focused: false
    });
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const interval = setInterval(async () => {
            const data = await getMetrics();
            if (data) {
                setMetrics(data);
                const newStatus = data.status || "Idle";
                setStatus(newStatus);
                
                // Show error message if status is Error
                if (newStatus === "Error" && data.error_log) {
                    setErrorMessage(data.error_log);
                } else if (newStatus !== "Error") {
                    setErrorMessage("");
                }
                
                // Update window focus status
                if (data.window_focused !== undefined) {
                    setMetrics(prev => ({ ...prev, window_focused: data.window_focused }));
                }

                setHistory(prev => {
                    const newHistory = [...prev, { step: data.total_steps, coverage: data.coverage }];
                    if (newHistory.length > 30) newHistory.shift();
                    return newHistory;
                });
            }
        }, 1000);
        return () => clearInterval(interval);
    }, []);


    const handleStart = async () => {
        try {
            setErrorMessage(""); // Clear previous errors
            
            // Focus the selected window before starting the test
            if (selectedWindow?.hwnd) {
                try {
                    await focusWindow(selectedWindow.hwnd);
                    console.log(`Focused window: ${selectedWindow.title}`);
                } catch (error) {
                    console.warn("Failed to focus window:", error);
                    // Continue with test even if focus fails
                }
            }
            
            const windowHwnd = selectedWindow?.hwnd || null;
            await startTest(genre, windowHwnd); 
        } catch (e) {
            const errorMsg = e?.response?.data?.detail || e?.message || "Failed to start test";
            setErrorMessage(errorMsg);
            alert("Failed to start test: " + errorMsg);
        }
    };

    const handleStop = async () => {
        try { 
            await stopTest(); 
        } catch (e) {
            const errorMsg = e?.response?.data?.detail || e?.message || "Failed to stop test";
            alert("Failed to stop test: " + errorMsg);
        }
    };

    const handleResetStatus = async () => {
        try {
            await resetStatus();
            setErrorMessage("");
            setStatus("Idle");
        } catch (e) {
            const errorMsg = e?.response?.data?.detail || e?.message || "Failed to reset status";
            alert("Failed to reset status: " + errorMsg);
        }
    };

    const handleGenreChange = (newGenre) => {
        setGenre(newGenre);
    };

    const handleWindowSelect = (window) => {
        setSelectedWindow(window);
    };

    return (
        <div className="min-h-screen bg-[#141414] text-white selection:bg-[#E50914] selection:text-white">
            {/* Navbar */}
            <nav className="fixed top-0 w-full z-50 transition-all duration-300 bg-gradient-to-b from-black/80 to-transparent pb-6 pt-4 px-8">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-1">
                        <span className="text-[#E50914] font-bold text-3xl tracking-tighter">PROJECTX</span>
                    </div>
                    {onLogout && (
                        <button
                            onClick={onLogout}
                            className="px-4 py-2 bg-[#E50914]/20 hover:bg-[#E50914]/30 border border-[#E50914]/50 text-white rounded font-semibold flex items-center gap-2 transition-colors text-sm"
                            title="Logout"
                        >
                            <LogOut size={16} />
                            <span>Logout</span>
                        </button>
                    )}
                </div>
            </nav>

            <main className="pt-24 max-w-7xl mx-auto p-6 md:px-8 space-y-8">

                {/* Hero / Control Section */}
                <HeroControlPanel
                    status={status}
                    genre={genre}
                    onGenreChange={handleGenreChange}
                    onStart={handleStart}
                    onStop={handleStop}
                    selectedWindow={selectedWindow}
                    onWindowSelect={handleWindowSelect}
                    windowFocused={metrics.window_focused}
                    onResetStatus={handleResetStatus}
                />

                {/* Error Message Display */}
                {status === "Error" && errorMessage && (
                    <div className="glass-card p-4 bg-red-900/20 border border-red-500/50 rounded">
                        <div className="flex items-start justify-between gap-4">
                            <div className="flex items-start gap-3 flex-1">
                                <AlertOctagon className="text-red-500 mt-0.5 flex-shrink-0" size={20} />
                                <div className="flex-1">
                                    <h3 className="text-red-400 font-semibold mb-1">Test Error</h3>
                                    <p className="text-red-300 text-sm">{errorMessage}</p>
                                </div>
                            </div>
                            <button
                                onClick={handleResetStatus}
                                className="px-3 py-1.5 bg-red-600/50 hover:bg-red-600/70 text-white text-xs rounded font-semibold transition-colors flex items-center gap-2 flex-shrink-0"
                                title="Reset status to Idle"
                            >
                                <RefreshCw size={14} />
                                Reset
                            </button>
                        </div>
                    </div>
                )}

                {/* Trending / Metrics Row */}
                <div>
                    <h2 className="text-white text-xl font-bold mb-4">Live Performance Metrics</h2>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <MetricCard
                            title="State Coverage"
                            value={metrics.coverage.toLocaleString()}
                            subValue="Uniques Found"
                            icon={Layers}
                            color="red"
                        />
                        <MetricCard
                            title="Critical Failures"
                            value={metrics.crashes}
                            subValue="Crashes/Freezes"
                            icon={AlertOctagon}
                            color="red"
                        />
                        <MetricCard
                            title="Active Model"
                            value={metrics.current_algorithm}
                            subValue="Architecture"
                            icon={Cpu}
                            color="white"
                        />
                        <MetricCard
                            title="Total Steps"
                            value={metrics.total_steps}
                            subValue="Training Loops"
                            icon={Film}
                            color="white"
                        />
                    </div>
                </div>

                {/* Chart Section */}
                <div className="glass-card p-6">
                    <h2 className="text-white text-lg font-bold mb-6">Learning Curve</h2>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={history}>
                                <defs>
                                    <linearGradient id="colorCoverage" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#E50914" stopOpacity={0.5} />
                                        <stop offset="95%" stopColor="#E50914" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                <XAxis
                                    dataKey="step"
                                    stroke="#666"
                                    tick={{ fill: '#666', fontSize: 12 }}
                                    tickLine={false}
                                    axisLine={false}
                                />
                                <YAxis
                                    stroke="#666"
                                    tick={{ fill: '#666', fontSize: 12 }}
                                    tickLine={false}
                                    axisLine={false}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1f1f1f',
                                        border: 'none',
                                        borderRadius: '4px',
                                        color: '#fff'
                                    }}
                                    itemStyle={{ color: '#fff' }}
                                    cursor={{ stroke: '#E50914', strokeWidth: 1 }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="coverage"
                                    stroke="#E50914"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorCoverage)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

            </main>
        </div>
    );
};

export default Dashboard;
