
'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Sidebar from './Sidebar';

export default function MainLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const pathname = usePathname();
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        // Simple auth check
        const token = localStorage.getItem('pb_token');
        if (!token && pathname !== '/login') {
            router.push('/login');
        } else {
            setIsAuthenticated(true);
        }
    }, [router, pathname]);

    if (!isAuthenticated && pathname !== '/login') {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-50">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-[#E23744]"></div>
            </div>
        );
    }

    // Login page doesn't get the sidebar layout
    if (pathname === '/login') {
        return <>{children}</>;
    }

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 flex flex-col md:flex-row">
            <Sidebar />
            <main className="flex-1 md:ml-20 p-4 md:p-8 pb-32 md:pb-8 min-h-screen">
                <div className="max-w-7xl mx-auto animate-fade-in mb-10 md:mb-0">
                    {children}
                </div>
            </main>
        </div>
    );
}
