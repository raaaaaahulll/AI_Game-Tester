import React, { useState } from 'react';
import { Eye, EyeOff, UserPlus, Mail, User, Lock } from 'lucide-react';
import { motion } from 'framer-motion';

const Register = ({ onRegister, onSwitchToLogin }) => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        setError(''); // Clear error on input change
        setSuccess(''); // Clear success on input change
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        
        // Validation
        if (!formData.username.trim() || !formData.email.trim() || !formData.password.trim() || !formData.confirmPassword.trim()) {
            setError('Please fill in all fields');
            return;
        }

        // Username validation (alphanumeric, 3-20 chars)
        if (!/^[a-zA-Z0-9_]{3,20}$/.test(formData.username)) {
            setError('Username must be 3-20 characters and contain only letters, numbers, and underscores');
            return;
        }

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            setError('Please enter a valid email address');
            return;
        }

        // Password validation (minimum 6 characters)
        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters long');
            return;
        }

        // Password confirmation
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        // Check if username or email already exists
        const users = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
        if (users.some(u => u.username === formData.username)) {
            setError('Username already exists');
            return;
        }
        if (users.some(u => u.email === formData.email)) {
            setError('Email already registered');
            return;
        }

        // Register user
        const newUser = {
            username: formData.username,
            email: formData.email,
            password: formData.password // In production, this should be hashed
        };

        users.push(newUser);
        localStorage.setItem('registeredUsers', JSON.stringify(users));

        setSuccess('Account created successfully! Redirecting to login...');
        
        // Auto-login after registration
        setTimeout(() => {
            const authData = {
                username: newUser.username,
                email: newUser.email,
                isAuthenticated: true
            };
            sessionStorage.setItem('auth', JSON.stringify(authData));
            onRegister(authData);
        }, 1500);
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
                    <p className="text-gray-400 text-sm">Create your account</p>
                </div>

                {/* Register Form */}
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
                                    placeholder="Choose a username"
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
                                    placeholder="Create a password (min. 6 characters)"
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

                        {/* Confirm Password Field */}
                        <div>
                            <label htmlFor="confirmPassword" className="block text-sm font-semibold text-gray-300 mb-2">
                                Confirm Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                <input
                                    type={showConfirmPassword ? 'text' : 'password'}
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    className="w-full bg-black/50 border border-white/30 text-white rounded px-10 py-3 pr-10 focus:outline-none focus:border-[#E50914] transition-colors"
                                    placeholder="Confirm your password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                                >
                                    {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                                </button>
                            </div>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="bg-red-900/20 border border-red-500/50 rounded p-3 text-red-300 text-sm">
                                {error}
                            </div>
                        )}

                        {/* Success Message */}
                        {success && (
                            <div className="bg-green-900/20 border border-green-500/50 rounded p-3 text-green-300 text-sm">
                                {success}
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            className="w-full px-8 py-3 bg-[#E50914] hover:bg-[#b2070f] text-white rounded font-bold flex items-center justify-center gap-2 transition-colors"
                        >
                            <UserPlus size={20} />
                            <span>Create Account</span>
                        </button>
                    </form>

                    {/* Switch to Login */}
                    <div className="mt-6 text-center">
                        <p className="text-gray-400 text-sm">
                            Already have an account?{' '}
                            <button
                                onClick={onSwitchToLogin}
                                className="text-[#E50914] hover:text-[#b2070f] font-semibold transition-colors"
                            >
                                Sign in
                            </button>
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default Register;

