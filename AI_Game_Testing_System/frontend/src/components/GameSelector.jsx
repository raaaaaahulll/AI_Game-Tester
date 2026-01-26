import React, { useState, useEffect } from 'react';
import { getActiveWindows } from '../services/api';
import { Monitor, RefreshCw } from 'lucide-react';

const GameSelector = ({ disabled, selectedWindow, onWindowSelect }) => {
    const [windows, setWindows] = useState([]);
    const [loading, setLoading] = useState(false);

    // Load windows function
    const loadWindows = async (force = false) => {
        if (loading && !force) {
            console.log("Already loading, skipping...");
            return;
        }
        
        console.log("Loading windows...");
        setLoading(true);
        try {
            const activeWindows = await getActiveWindows();
            console.log(`Loaded ${activeWindows?.length || 0} windows:`, activeWindows);
            setWindows(activeWindows || []);
        } catch (error) {
            console.error("Error fetching windows:", error);
            alert(`Failed to load windows: ${error.message || 'Unknown error'}`);
            setWindows([]);
        } finally {
            setLoading(false);
        }
    };

    // Load windows on mount
    useEffect(() => {
        loadWindows();
    }, []);

    const handleSelectChange = (e) => {
        const selectedValue = e.target.value;
        console.log("Selected value:", selectedValue);
        
        if (selectedValue === "" || selectedValue === "auto-detect") {
            onWindowSelect(null);
            return;
        }
        
        // Find the selected window
        const window = windows.find(w => `${w.pid}-${w.hwnd || 'none'}` === selectedValue);
        console.log("Found window:", window);
        if (window) {
            onWindowSelect(window);
        } else {
            console.warn("Window not found for value:", selectedValue);
        }
    };

    const getSelectValue = () => {
        if (selectedWindow) {
            return `${selectedWindow.pid}-${selectedWindow.hwnd || 'none'}`;
        }
        return "auto-detect";
    };

    return (
        <div className="relative flex items-center gap-2">
            <Monitor size={16} className="text-white/70" />
            <select
                value={getSelectValue()}
                onChange={handleSelectChange}
                onClick={() => loadWindows(true)}
                onFocus={() => loadWindows(true)}
                disabled={disabled || loading}
                className="bg-black/50 border border-white/30 text-white text-sm rounded px-3 py-3 pr-8 focus:outline-none focus:border-white font-bold tracking-wider transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-w-[200px] cursor-pointer"
            >
                <option value="auto-detect">GAME: Auto-detect</option>
                {loading && <option disabled>Loading windows...</option>}
                {!loading && windows.length === 0 && <option disabled>No windows found - Click refresh</option>}
                {windows.map((window, idx) => (
                    <option 
                        key={`${window.pid}-${window.hwnd || 'none'}-${idx}`}
                        value={`${window.pid}-${window.hwnd || 'none'}`}
                    >
                        {window.title} ({window.process_name})
                    </option>
                ))}
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
    );
};

export default GameSelector;
