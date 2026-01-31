import React, { useState } from 'react';
import { Eye, EyeOff, LogIn, Mail, User, Lock } from 'lucide-react';
import { motion } from 'framer-motion';

const Login = ({ onLogin, onSwitchToRegister }) => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        setError(''); // Clear error on input change
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        
        // Validation
        if (!formData.username.trim() || !formData.email.trim() || !formData.password.trim()) {
            setError('Please fill in all fields');
            return;
        }

        // Basic email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            setError('Please enter a valid email address');
            return;
        }

        // Check if user exists in localStorage
        const users = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
        const user = users.find(u => 
            (u.username === formData.username || u.email === formData.email) && 
            u.password === formData.password
        );

        if (!user) {
            setError('Invalid username/email or password');
            return;
        }

        // Login successful
        const authData = {
            username: user.username,
            email: user.email,
            isAuthenticated: true
        };

        if (rememberMe) {
            localStorage.setItem('auth', JSON.stringify(authData));
        } else {
            sessionStorage.setItem('auth', JSON.stringify(authData));
        }

        onLogin(authData);
    };

    return (
        <div className="min-h-screen bg-[#141414] text-white selection:bg-[#E50914] selection:text-white flex items-center justify-center p-6">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md"
            >
                {/* Logo/Brand */}
                <div className="text-center mb-8">
                    <h1 className="text-[#E50914] font-bold text-4xl tracking-tighter mb-2">PROJECTX</h1>
                    <p className="text-gray-400 text-sm">Sign in to continue</p>
                </div>

                {/* Login Form */}
                <div className="glass-card p-8">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Username Field */}
                        <div>
                            <label htmlFor="username" className="block text-sm font-semibold text-gray-300 mb-2">
                                Username
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    className="w-full bg-black/50 border border-white/30 text-white rounded px-10 py-3 focus:outline-none focus:border-[#E50914] transition-colors"
                                    placeholder="Enter your username"
                                />
                            </div>
                        </div>

                        {/* Email Field */}
                        <div>
                            <label htmlFor="email" className="block text-sm font-semibold text-gray-300 mb-2">
                                Email
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full bg-black/50 border border-white/30 text-white rounded px-10 py-3 focus:outline-none focus:border-[#E50914] transition-colors"
                                    placeholder="Enter your email"
                                />
                            </div>
                        </div>

                        {/* Password Field */}
                        <div>
                            <label htmlFor="password" className="block text-sm font-semibold text-gray-300 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="w-full bg-black/50 border border-white/30 text-white rounded px-10 py-3 pr-10 focus:outline-none focus:border-[#E50914] transition-colors"
                                    placeholder="Enter your password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                                >
                                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                                </button>
                            </div>
                        </div>

                        {/* Remember Me */}
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                id="rememberMe"
                                checked={rememberMe}
                                onChange={(e) => setRememberMe(e.target.checked)}
                                className="w-4 h-4 bg-black/50 border-white/30 rounded focus:ring-[#E50914] text-[#E50914]"
                            />
                            <label htmlFor="rememberMe" className="ml-2 text-sm text-gray-300">
                                Remember me / Stay logged in
                            </label>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="bg-red-900/20 border border-red-500/50 rounded p-3 text-red-300 text-sm">
                                {error}
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            className="w-full px-8 py-3 bg-[#E50914] hover:bg-[#b2070f] text-white rounded font-bold flex items-center justify-center gap-2 transition-colors"
                        >
                            <LogIn size={20} />
                            <span>Sign In</span>
                        </button>
                    </form>

                    {/* Switch to Register */}
                    <div className="mt-6 text-center">
                        <p className="text-gray-400 text-sm">
                            Don't have an account?{' '}
                            <button
                                onClick={onSwitchToRegister}
                                className="text-[#E50914] hover:text-[#b2070f] font-semibold transition-colors"
                            >
                                Sign up
                            </button>
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default Login;

