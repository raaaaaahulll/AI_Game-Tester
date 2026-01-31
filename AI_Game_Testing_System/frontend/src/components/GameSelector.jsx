import React, { useState, useEffect, useRef } from 'react';
import { getActiveWindows } from '../services/api';
import { Monitor, RefreshCw } from 'lucide-react';

const GameSelector = ({ disabled, selectedWindow, onWindowSelect }) => {
    const [windows, setWindows] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const selectRef = useRef(null);

    // Load windows function
    const loadWindows = async (force = false) => {
        if (loading && !force) {
            return;
        }
        
        setLoading(true);
        try {
            console.log("Fetching active windows from API...");
            const activeWindows = await getActiveWindows();
            console.log("API Response:", activeWindows);
            const windowsList = Array.isArray(activeWindows) ? activeWindows : [];
            console.log(`Successfully loaded ${windowsList.length} windows`);
            
            if (windowsList.length > 0) {
                console.log("Window list:", windowsList.map(w => ({ 
                    title: w.title, 
                    process: w.process_name, 
                    hwnd: w.hwnd 
                })));
            } else {
                console.warn("No windows returned from API. Check backend logs.");
            }
            
            setWindows(windowsList);
            
            // If we have a selected window, verify it still exists in the new list
            if (selectedWindow && windowsList.length > 0) {
                const stillExists = windowsList.some(w => 
                    w.pid === selectedWindow.pid && 
                    (w.hwnd === selectedWindow.hwnd || (!w.hwnd && !selectedWindow.hwnd))
                );
                if (!stillExists) {
                    // Selected window no longer exists, reset to auto-detect
                    onWindowSelect(null);
                }
            }
        } catch (error) {
            console.error("Error fetching windows:", error);
            console.error("Error details:", error.response || error.message);
            console.error("Full error:", error);
            setWindows([]);
            // Show alert when manually refreshing
            if (force) {
                const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
                let alertMsg = `Failed to load windows: ${errorMsg}\n\n`;
                alertMsg += `Troubleshooting steps:\n`;
                alertMsg += `1. Check backend server is running (http://localhost:8000)\n`;
                alertMsg += `2. Check browser console (F12) for network errors\n`;
                alertMsg += `3. Check backend logs (backend/logs/app.log)\n`;
                alertMsg += `4. Try installing pywin32: pip install pywin32\n`;
                alertMsg += `5. Verify you have visible/minimized windows open\n`;
                alert(alertMsg);
            }
        } finally {
            setLoading(false);
        }
    };

    // Load windows on mount
    useEffect(() => {
        loadWindows();
    }, []);

    const handleSelectChange = async (e) => {
        const selectedValue = e.target.value;
        
        if (selectedValue === "" || selectedValue === "auto-detect") {
            onWindowSelect(null);
            return;
        }
        
        // Find the selected window
        const window = windows.find(w => {
            const windowValue = `${w.pid}-${w.hwnd || 'none'}`;
            return windowValue === selectedValue;
        });
        
        if (window) {
            onWindowSelect(window);
            // Note: Window focus is now handled when "Start Testing" is clicked
        } else {
            console.warn("Window not found for value:", selectedValue);
            onWindowSelect(null);
        }
    };

    const handleSelectClick = () => {
        // Always reload windows when opening dropdown to get fresh list
        if (!isOpen && !loading) {
            loadWindows(true);
        }
        setIsOpen(!isOpen);
    };

    const handleSelectBlur = () => {
        // Small delay to allow option click to register
        setTimeout(() => {
            setIsOpen(false);
        }, 200);
    };

    const getSelectValue = () => {
        if (selectedWindow) {
            const value = `${selectedWindow.pid}-${selectedWindow.hwnd || 'none'}`;
            // Verify the selected window still exists in the current windows list
            const exists = windows.some(w => {
                const windowValue = `${w.pid}-${w.hwnd || 'none'}`;
                return windowValue === value;
            });
            if (exists) {
                return value;
            }
        }
        return "auto-detect";
    };

    return (
        <div className="flex flex-col gap-1">
            <div className="relative flex items-center gap-2">
                <Monitor size={16} className="text-white/70" />
                <select
                    ref={selectRef}
                    value={getSelectValue()}
                    onChange={handleSelectChange}
                    onClick={handleSelectClick}
                    onBlur={handleSelectBlur}
                    disabled={disabled || loading}
                    className="bg-black/50 border border-white/30 text-white text-sm rounded px-3 py-3 pr-8 focus:outline-none focus:border-white font-bold tracking-wider transition-colors disabled:opacity-50 disabled:cursor-not-allowed w-[280px] cursor-pointer truncate"
                >
                    <option value="auto-detect">GAME: Auto-detect</option>
                    {loading && <option disabled>Loading windows...</option>}
                    {!loading && windows.length === 0 && <option disabled>No windows found - Click refresh</option>}
                    {windows.map((window, idx) => {
                        const windowValue = `${window.pid}-${window.hwnd || 'none'}`;
                        const displayTitle = (window.title || 'Untitled Window').substring(0, 25);
                        const displayProcess = (window.process_name || 'Unknown Process').substring(0, 15);
                        return (
                            <option 
                                key={`${window.pid}-${window.hwnd || 'none'}-${idx}`}
                                value={windowValue}
                            >
                                {displayTitle}{displayTitle.length >= 25 ? '...' : ''} ({displayProcess})
                            </option>
                        );
                    })}
                </select>
                <button
                    onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        loadWindows(true);
                    }}
                    disabled={disabled || loading}
                    className="p-2 hover:bg-white/10 rounded transition-colors disabled:opacity-50"
                    title="Refresh windows list"
                >
                    <RefreshCw size={16} className={`text-white/70 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>
            {selectedWindow && (
                <div className="flex items-center gap-1.5 text-xs text-green-400 ml-6">
                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                    <span className="font-semibold truncate max-w-[260px]">Game window selected: {selectedWindow.title || selectedWindow.process_name}</span>
                </div>
            )}
        </div>
    );
};

export default GameSelector;
