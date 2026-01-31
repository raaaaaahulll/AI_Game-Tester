import React from 'react';
import { Play, Square, Activity } from 'lucide-react';
import GameSelector from './GameSelector';

const HeroControlPanel = ({ 
    status, 
    genre, 
    onGenreChange, 
    onStart, 
    onStop,
    selectedWindow,
    onWindowSelect,
    windowFocused,
    onResetStatus 
}) => {
    const isTraining = status.startsWith("Training");

    return (
        <div className="relative rounded-xl overflow-hidden min-h-[400px] border border-white/10 flex flex-col justify-end p-8 bg-[#1f1f1f]">
            {/* Background Abstract */}
            <div className="absolute inset-0 bg-black">
                <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/50 to-transparent z-10" />
                <div className="absolute inset-0 opacity-20 bg-[url('https://c4.wallpaperflare.com/wallpaper/586/603/742/minimalism-4k-for-mac-desktop-wallpaper-preview.jpg')] bg-cover bg-center" />
            </div>

            <div className="relative z-20 max-w-2xl">
                <h1 className="text-5xl md:text-6xl font-black mb-4 tracking-tighter text-white drop-shadow-lg">
                    GAME TESTER <span className="text-[#E50914]">PRO</span>
                </h1>
                <p className="text-lg text-gray-300 mb-6 drop-shadow-md">
                    Autonomous agentic verification system. Powered by advanced Reinforcement Learning algorithms including PPO, DQN, and SAC.
                </p>

                {/* Control Row */}
                <div className="flex flex-col sm:flex-row gap-4 items-center">
                    <button
                        onClick={onStart}
                        disabled={isTraining}
                        className="w-full sm:w-auto px-8 py-3 bg-[#E50914] hover:bg-[#b2070f] text-white rounded font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Play size={24} fill="currentColor" />
                        <span>Start Testing</span>
                    </button>

                    <GameSelector 
                        disabled={isTraining}
                        selectedWindow={selectedWindow}
                        onWindowSelect={onWindowSelect}
                    />

                    <div className="flex items-center gap-3 ml-2 flex-wrap">
                        <select
                            value={genre}
                            onChange={(e) => onGenreChange(e.target.value)}
                            disabled={isTraining}
                            className="bg-black/50 border border-white/30 text-white text-sm rounded px-3 py-3 focus:outline-none focus:border-white uppercase font-bold tracking-wider"
                        >
                            <option value="platformer">Genre: Platformer</option>
                            <option value="fps">Genre: FPS</option>
                            <option value="racing">Genre: Racing</option>
                            <option value="rpg">Genre: RPG</option>
                        </select>
                    </div>

                    <button
                        onClick={onStop}
                        disabled={!isTraining}
                        className="w-full sm:w-auto px-8 py-3 bg-[#6d6d6e]/60 hover:bg-[#6d6d66]/80 text-white rounded font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
                    >
                        <Square size={24} fill="currentColor" />
                        <span>Stop</span>
                    </button>
                </div>

                <div className="mt-6 flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-sm font-semibold text-gray-400">
                        <Activity size={16} className={status !== "Idle" ? "text-green-500 animate-pulse" : "text-gray-600"} />
                        <span>STATUS: <span className="text-white">{status}</span></span>
                    </div>
                    {isTraining && selectedWindow && (
                        <div className="flex items-center gap-2 text-sm font-semibold">
                            {windowFocused ? (
                                <>
                                    <span>🎮</span>
                                    <span className="text-green-400">Game Window Focused</span>
                                </>
                            ) : (
                                <>
                                    <span>⚠️</span>
                                    <span className="text-yellow-400">Game Window Not Focused</span>
                                </>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default HeroControlPanel;

