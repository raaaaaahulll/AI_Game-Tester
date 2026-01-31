import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const startTest = async (genre, windowHwnd = null) => {
    try {
        const response = await axios.post(`${API_URL}/start-test`, { 
            genre,
            window_hwnd: windowHwnd
        });
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export const stopTest = async () => {
    try {
        const response = await axios.post(`${API_URL}/stop-test`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export const getMetrics = async () => {
    try {
        const response = await axios.get(`${API_URL}/metrics`);
        return response.data;
    } catch (error) {
        console.error("Error fetching metrics", error);
        return null;
    }
};

export const resetStatus = async () => {
    try {
        const response = await axios.post(`${API_URL}/reset-status`);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

// Windows API
export const getActiveWindows = async () => {
    try {
        const response = await axios.get(`${API_URL}/windows`);
        return response.data;
    } catch (error) {
        console.error("Error fetching active windows", error);
        return [];
    }
};

export const focusWindow = async (hwnd) => {
    try {
        const response = await axios.post(`${API_URL}/windows/${hwnd}/focus`);
        return response.data;
    } catch (error) {
        console.error("Error focusing window", error);
        throw error.response ? error.response.data : error;
    }
};