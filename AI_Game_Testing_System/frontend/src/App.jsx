import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Register from './components/Register';

function App() {
  const [auth, setAuth] = useState(null);
  const [showRegister, setShowRegister] = useState(false);

  // Removed auto-authentication check - always show login page first
  // User must explicitly log in each time

  const handleLogin = (authData) => {
    setAuth(authData);
    setShowRegister(false);
  };

  const handleRegister = (authData) => {
    setAuth(authData);
    setShowRegister(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth');
    sessionStorage.removeItem('auth');
    setAuth(null);
  };

  // Show login/register if not authenticated
  if (!auth || !auth.isAuthenticated) {
    if (showRegister) {
      return <Register onRegister={handleRegister} onSwitchToLogin={() => setShowRegister(false)} />;
    }
    return <Login onLogin={handleLogin} onSwitchToRegister={() => setShowRegister(true)} />;
  }

  // Show dashboard if authenticated
  return <Dashboard onLogout={handleLogout} />;
}

export default App
