
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase, apiRequest } from '@/lib/supabase';

// Define the Login Response here since we don't have it in types yet
interface LoginResponse {
    token: string;
    restaurant_id: string;
    restaurant_name: string;
}

export default function LoginPage() {
    const router = useRouter();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Call the custom auth endpoint
            const res = await apiRequest<LoginResponse>('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password }),
            });

            // Store token and user info
            if (res.token) {
                localStorage.setItem('pb_token', res.token);
                localStorage.setItem('pb_restaurant_id', res.restaurant_id);
                localStorage.setItem('pb_restaurant_name', res.restaurant_name);

                // Redirect to dashboard
                router.push('/');
            } else {
                throw new Error('Invalid response');
            }
        } catch (err: any) {
            console.error('Login failed:', err);
            setError('Invalid username or password. Try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen flex items-center justify-center bg-gray-50 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-red-500/5 rounded-full blur-[120px]"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-orange-500/5 rounded-full blur-[120px]"></div>
            </div>

            <div className="relative z-10 w-full max-w-md px-4">
                <div className="bg-white border border-gray-100 rounded-2xl p-6 md:p-8 shadow-2xl">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-[#E23744] to-[#C21F2D] rounded-xl mb-4 shadow-lg shadow-red-500/20">
                            <span className="text-2xl font-bold text-white">⚡</span>
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome Back</h1>
                        <p className="text-gray-500 text-sm">Sign in to manage your restaurant's marketing.</p>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleLogin} className="space-y-4">
                        {error && (
                            <div className="bg-red-50 border border-red-100 text-[#E23744] text-sm p-3 rounded-lg text-center animate-shake">
                                {error}
                            </div>
                        )}

                        <div>
                            <label className="block text-xs font-bold text-gray-400 mb-1.5 ml-1 tracking-wide">USERNAME</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#E23744] focus:ring-1 focus:ring-[#E23744]/20 transition-all shadow-sm"
                                placeholder="Enter your username"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-gray-400 mb-1.5 ml-1 tracking-wide">PASSWORD</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#E23744] focus:ring-1 focus:ring-[#E23744]/20 transition-all shadow-sm"
                                placeholder="••••••••"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full bg-[#E23744] hover:bg-[#d12c39] text-white font-bold py-3.5 rounded-xl shadow-lg shadow-red-500/20 transition-all transform active:scale-[0.98] ${loading ? 'opacity-70 cursor-not-allowed' : 'hover:-translate-y-0.5'
                                }`}
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                    Signing in...
                                </span>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    {/* Footer */}
                    <div className="mt-6 text-center">
                        <p className="text-xs text-gray-500">
                            Need help? <a href="#" className="text-[#E23744] hover:text-[#d12c39] font-medium">Contact Support</a>
                        </p>
                    </div>
                </div>

                <p className="text-center text-gray-400 text-xs mt-8">
                    &copy; 2024 PocketBuzz Inc.
                </p>
            </div>
        </main>
    );
}
