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
            const activeWindows = await getActiveWindows();
            const windowsList = activeWindows || [];
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
            setWindows([]);
            // Don't show alert on every error, just log it
            if (force) {
                alert(`Failed to load windows: ${error.message || 'Unknown error'}`);
            }
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
        } else {
            console.warn("Window not found for value:", selectedValue);
            onWindowSelect(null);
        }
    };

    const handleSelectClick = () => {
        // Only reload if dropdown is opening and we don't have windows
        if (!isOpen && windows.length === 0 && !loading) {
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
        <div className="relative flex items-center gap-2">
            <Monitor size={16} className="text-white/70" />
            <select
                ref={selectRef}
                value={getSelectValue()}
                onChange={handleSelectChange}
                onClick={handleSelectClick}
                onBlur={handleSelectBlur}
                disabled={disabled || loading}
                className="bg-black/50 border border-white/30 text-white text-sm rounded px-3 py-3 pr-8 focus:outline-none focus:border-white font-bold tracking-wider transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-w-[200px] cursor-pointer"
            >
                <option value="auto-detect">GAME: Auto-detect</option>
                {loading && <option disabled>Loading windows...</option>}
                {!loading && windows.length === 0 && <option disabled>No windows found - Click refresh</option>}
                {windows.map((window, idx) => {
                    const windowValue = `${window.pid}-${window.hwnd || 'none'}`;
                    const displayTitle = window.title || 'Untitled Window';
                    const displayProcess = window.process_name || 'Unknown Process';
                    return (
                        <option 
                            key={`${window.pid}-${window.hwnd || 'none'}-${idx}`}
                            value={windowValue}
                        >
                            {displayTitle} ({displayProcess})
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
    );
};

export default GameSelector;
