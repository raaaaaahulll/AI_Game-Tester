import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Register from './components/Register';
import { isAuthenticated, getAuth } from './utils/auth';

function App() {
  const [auth, setAuth] = useState(null);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    // Check if user is already authenticated
    if (isAuthenticated()) {
      setAuth(getAuth());
    }
  }, []);

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
