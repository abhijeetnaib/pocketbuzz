'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
    const [stats, setStats] = useState({
        orders: 0,
        revenue: 0,
        customers: 0,
        avgOrderValue: 0
    });
    const [recentCampaigns, setRecentCampaigns] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const loadDashboard = async () => {
            const restaurantId = localStorage.getItem('pb_restaurant_id');
            if (!restaurantId) return;

            try {
                // 1. Stats (Last 30 Days for better data)
                const thirtyDaysAgo = new Date();
                thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

                const { data: orders } = await supabase
                    .from('universal_records')
                    .select('bill_amount, client_phone')
                    .eq('restaurant_id', restaurantId)
                    .gte('visit_date', thirtyDaysAgo.toISOString().split('T')[0]);

                if (orders) {
                    const uniqueCustomers = new Set(orders.map(o => o.client_phone)).size;
                    const totalRevenue = orders.reduce((sum, o) => sum + (o.bill_amount || 0), 0);

                    setStats({
                        orders: orders.length,
                        revenue: totalRevenue,
                        customers: uniqueCustomers,
                        avgOrderValue: orders.length ? Math.round(totalRevenue / orders.length) : 0
                    });
                }

                // 2. Recent Campaigns
                const { data: campaigns } = await supabase
                    .from('campaign_suggestions')
                    .select('*')
                    .eq('restaurant_id', restaurantId)
                    .order('created_at', { ascending: false })
                    .limit(5); // Show top 5

                if (campaigns) setRecentCampaigns(campaigns);

            } catch (err) {
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        loadDashboard();
    }, []);

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <div className="w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">
                        Dashboard
                    </h1>
                    <p className="text-gray-500 text-sm mt-1">Overview of your restaurant's performance</p>
                </div>
                <button
                    onClick={() => router.push('/campaigns/new')}
                    className="bg-[#E23744] hover:bg-[#d12c39] text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md shadow-red-500/20 transition-all active:scale-95 flex items-center gap-2"
                >
                    <span>+</span> New Campaign
                </button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                    label="Revenue (30d)"
                    value={`₹${(stats.revenue / 1000).toFixed(1)}k`}
                    icon="💰"
                    trend="+12%"
                    color="text-green-600"
                />
                <StatCard
                    label="Orders"
                    value={stats.orders.toString()}
                    icon="🧾"
                    trend="+8%"
                    color="text-blue-600"
                />
                <StatCard
                    label="Active Customers"
                    value={stats.customers.toString()}
                    icon="👥"
                    trend="+5%"
                    color="text-purple-600"
                />
                <StatCard
                    label="Avg. Order Value"
                    value={`₹${stats.avgOrderValue}`}
                    icon="💎"
                    trend="-2%"
                    color="text-orange-600"
                />
            </div>

            {/* Recent Campaigns Section */}
            <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold text-gray-900">Recent Campaigns</h2>
                    <button
                        onClick={() => router.push('/analytics')}
                        className="text-xs text-[#E23744] hover:text-[#d12c39] font-medium"
                    >
                        View Analytics →
                    </button>
                </div>

                <div className="space-y-3">
                    {recentCampaigns.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            No campaigns yet. Start your first one!
                        </div>
                    ) : (
                        recentCampaigns.map((camp) => (
                            <div
                                key={camp.id}
                                onClick={() => router.push(`/campaign/${camp.id}`)}
                                className="group flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:border-red-200 hover:shadow-md transition-all cursor-pointer"
                            >
                                <div className="flex items-center gap-3 md:gap-4 min-w-0">
                                    {/* Thumbnail */}
                                    <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg bg-gray-100 overflow-hidden relative flex-shrink-0 border border-gray-100 shadow-sm">
                                        {camp.generated_image_url ? (
                                            <img src={camp.generated_image_url} alt="" className="w-full h-full object-cover" />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-lg text-gray-400 font-bold bg-gray-50 uppercase tracking-tighter">📷</div>
                                        )}
                                    </div>

                                    {/* Text Info */}
                                    <div className="min-w-0">
                                        <h3 className="font-bold text-gray-900 text-sm md:text-base truncate group-hover:text-[#E23744] transition-colors leading-tight">
                                            {camp.item_name || camp.generated_caption?.substring(0, 30) || 'Untitled Campaign'}
                                        </h3>
                                        <div className="flex items-center gap-1.5 mt-0.5 md:mt-1">
                                            <span className="text-[9px] md:text-[10px] uppercase font-bold bg-gray-50 text-gray-500 px-1.5 py-0.5 rounded border border-gray-200 truncate max-w-[80px] md:max-w-none">
                                                {camp.strategy_type?.replace('_', ' ')}
                                            </span>
                                            <span className="text-[10px] md:text-xs text-gray-400 font-medium truncate">• {new Date(camp.created_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Status Badge */}
                                <div className="flex items-center gap-4">
                                    <StatusBadge status={camp.status} />
                                    <span className="text-gray-400 group-hover:translate-x-1 transition-transform">→</span>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}

// Sub-components
function StatCard({ label, value, icon, trend, color }: any) {
    const isPositive = trend.startsWith('+');
    return (
        <div className="bg-white border border-gray-100 p-3 md:p-5 rounded-2xl hover:shadow-md transition-all group cursor-default shadow-sm">
            <div className="flex justify-between items-start mb-1 md:mb-2">
                <span className="text-xl md:text-2xl group-hover:scale-110 transition-transform duration-300">{icon}</span>
                <span className={`text-[10px] md:text-xs font-mono px-1.5 py-0.5 rounded ${isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {trend}
                </span>
            </div>
            <div className={`text-xl md:text-2xl font-bold mb-0.5 md:mb-1 ${color}`}>{value}</div>
            <div className="text-[10px] md:text-xs text-gray-500 font-medium uppercase tracking-tight">{label}</div>
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    const styles: any = {
        PENDING: 'bg-yellow-100 text-yellow-700 border-yellow-200',
        APPROVED: 'bg-blue-100 text-blue-700 border-blue-200',
        SENT: 'bg-green-100 text-green-700 border-green-200',
        FAILED: 'bg-red-100 text-red-700 border-red-200',
    };

    return (
        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border ${styles[status] || styles.PENDING}`}>
            {status}
        </span>
    );
}
