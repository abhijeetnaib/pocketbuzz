
'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useState } from 'react';

const Sidebar = () => {
    const pathname = usePathname();
    const router = useRouter();
    const [collapsed, setCollapsed] = useState(true);

    // Update paths as needed based on actual routes
    const navItems = [
        { label: 'Overview', icon: '📊', path: '/' },
        { label: 'New Campaign', icon: '📢', path: '/campaigns/new' },
        { label: 'Analytics', icon: '📈', path: '/analytics' },
        { label: 'Settings', icon: '⚙️', path: '/settings' },
    ];

    const handleLogout = () => {
        localStorage.removeItem('pb_token');
        localStorage.removeItem('pb_restaurant_id');
        window.location.href = '/login';
    };

    return (
        <aside className="fixed bottom-0 left-0 right-0 md:top-0 md:left-0 md:bottom-0 md:right-auto md:w-20 bg-white/90 border-t md:border-r border-gray-100 z-50 flex md:flex-col justify-between items-center h-[72px] md:h-screen py-2 md:py-8 backdrop-blur-xl shadow-[0_-4px_20px_rgba(0,0,0,0.03)] md:shadow-none">
            {/* Logo */}
            <div className="hidden md:flex flex-col items-center mb-8">
                <div className="w-10 h-10 bg-gradient-to-br from-[#E23744] to-[#C21F2D] rounded-xl flex items-center justify-center shadow-lg shadow-red-500/20">
                    <span className="text-xl font-bold text-white">⚡</span>
                </div>
            </div>

            {/* Nav Items */}
            <nav className="flex flex-1 md:flex-col justify-around md:justify-start w-full md:gap-4 px-2 md:px-0">
                {navItems.map((item) => {
                    const isActive = pathname === item.path;
                    return (
                        <button
                            key={item.path}
                            onClick={() => router.push(item.path)}
                            className={`group relative flex flex-col items-center justify-center p-2 rounded-xl transition-all min-w-[64px] ${isActive
                                ? 'text-[#E23744] bg-red-50 font-bold'
                                : 'text-gray-400 hover:text-gray-900 hover:bg-gray-100 font-medium'
                                }`}
                        >
                            <span className="text-xl mb-0.5 md:mb-0 grayscale-[0.5] group-hover:grayscale-0 transition-all">{item.icon}</span>
                            <span className="text-[10px] md:hidden uppercase tracking-tighter">{item.label}</span>

                            {/* Tooltip for Desktop */}
                            <div className="hidden md:group-hover:block absolute left-full ml-4 bg-white text-gray-900 text-xs px-2 py-1 rounded whitespace-nowrap border border-gray-200 shadow-md opacity-0 group-hover:opacity-100 transition-opacity z-50">
                                {item.label}
                            </div>
                        </button>
                    );
                })}
            </nav>

            {/* User / Logout */}
            <div className="hidden md:flex flex-col gap-4">
                <button
                    onClick={handleLogout}
                    className="w-10 h-10 rounded-full bg-gray-50 hover:bg-red-50 hover:text-[#E23744] text-gray-400 flex items-center justify-center transition-all border border-transparent hover:border-red-100"
                    title="Logout"
                >
                    🚪
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
