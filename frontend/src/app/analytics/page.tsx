
'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'next/navigation';

export default function AnalyticsPage() {
    const [stats, setStats] = useState<any>(null);
    const [topItems, setTopItems] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const loadAnalytics = async () => {
            const restaurantId = localStorage.getItem('pb_restaurant_id');
            if (!restaurantId) return;

            try {
                // Fetch last 1000 records for analysis
                const { data: records } = await supabase
                    .from('universal_records')
                    .select('*')
                    .eq('restaurant_id', restaurantId)
                    .order('visit_date', { ascending: false })
                    .limit(1000);

                if (!records) return;

                // 1. Basic Stats
                const totalRevenue = records.reduce((sum, r) => sum + (r.bill_amount || 0), 0);
                const uniqueCustomers = new Set(records.map(r => r.client_phone)).size;

                // 2. Top Items Analysis
                const itemMap: Record<string, number> = {};
                records.forEach(r => {
                    // Rudimentary parsing of item_ordered string if it contains multiple
                    // Assuming format "Item1, Item2" or just "Item1"
                    if (r.item_ordered) {
                        const items = r.item_ordered.split(',').map((i: string) => i.trim());
                        items.forEach((item: string) => {
                            if (item) itemMap[item] = (itemMap[item] || 0) + 1;
                        });
                    }
                });

                const sortedItems = Object.entries(itemMap)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 5) // Top 5
                    .map(([name, count]) => ({ name, count }));

                // 3. Customer Retention (Repeat vs New)
                // Simplified logic: If phone appears > 1 in this batch, they are repeat
                const customerCounts: Record<string, number> = {};
                records.forEach(r => {
                    if (r.client_phone) customerCounts[r.client_phone] = (customerCounts[r.client_phone] || 0) + 1;
                });

                const repeatCustomers = Object.values(customerCounts).filter(c => c > 1).length;
                const repeatRate = uniqueCustomers ? Math.round((repeatCustomers / uniqueCustomers) * 100) : 0;

                setStats({
                    totalRevenue,
                    totalOrders: records.length,
                    uniqueCustomers,
                    repeatRate,
                    avgOrderValue: Math.round(totalRevenue / records.length)
                });
                setTopItems(sortedItems);

            } catch (err) {
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        loadAnalytics();
    }, []);

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <div className="w-8 h-8 border-2 border-[#E23744] border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!stats) {
        return <div className="text-center p-8 text-gray-500">No data available yet.</div>;
    }

    return (
        <div className="space-y-8 animate-slide-up pb-10">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button
                    onClick={() => router.back()}
                    className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-900 transition-colors"
                >
                    ←
                </button>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
                    <p className="text-gray-500 text-sm">Deep dive into your restaurant's data</p>
                </div>
            </div>

            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white border border-gray-100 p-4 md:p-6 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-gray-500 text-[10px] md:text-xs font-bold uppercase tracking-wider mb-1 md:mb-2">Total Revenue</p>
                    <h3 className="text-2xl md:text-3xl font-bold text-green-600">₹{(stats.totalRevenue / 1000).toFixed(1)}k</h3>
                    <p className="text-[10px] md:text-xs text-gray-400 mt-1 md:mt-2">Based on last 1000 orders</p>
                </div>
                <div className="bg-white border border-gray-100 p-4 md:p-6 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-gray-500 text-[10px] md:text-xs font-bold uppercase tracking-wider mb-1 md:mb-2">Repeat Rate</p>
                    <h3 className="text-2xl md:text-3xl font-bold text-blue-600">{stats.repeatRate}%</h3>
                    <p className="text-[10px] md:text-xs text-gray-400 mt-1 md:mt-2">Customers who ordered more than once</p>
                </div>
                <div className="bg-white border border-gray-100 p-4 md:p-6 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-gray-500 text-[10px] md:text-xs font-bold uppercase tracking-wider mb-1 md:mb-2">Avg. Order Value</p>
                    <h3 className="text-2xl md:text-3xl font-bold text-purple-600">₹{stats.avgOrderValue}</h3>
                    <p className="text-[10px] md:text-xs text-gray-400 mt-1 md:mt-2">Per bill average</p>
                </div>
            </div>

            {/* Top Items List */}
            <div className="bg-white border border-gray-100 rounded-2xl p-4 md:p-6 shadow-sm">
                <h2 className="text-lg font-bold text-gray-900 mb-4 md:mb-6 flex items-center gap-2">
                    🏆 Top Selling Items
                </h2>
                <div className="space-y-4 md:space-y-6">
                    {topItems.map((item, index) => (
                        <div key={item.name} className="flex items-center gap-4 group">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${index === 0 ? 'bg-yellow-100 text-yellow-700' :
                                index === 1 ? 'bg-gray-100 text-gray-600' :
                                    index === 2 ? 'bg-orange-100 text-orange-700' : 'bg-gray-50 text-gray-400'
                                }`}>
                                #{index + 1}
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between mb-2">
                                    <span className="font-medium text-gray-900 group-hover:text-[#E23744] transition-colors">{item.name}</span>
                                    <span className="text-gray-500 text-sm font-mono">{item.count} orders</span>
                                </div>
                                {/* Progress Bar */}
                                <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-[#E23744] to-orange-500 rounded-full"
                                        style={{ width: `${(item.count / topItems[0].count) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* AI Insight */}
            <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-100 p-6 rounded-2xl shadow-sm">
                <div className="flex items-start gap-4">
                    <div className="text-2xl p-2 bg-white rounded-lg shadow-sm">💡</div>
                    <div>
                        <h3 className="font-bold text-[#E23744] mb-1">AI Insight</h3>
                        <p className="text-sm text-gray-600 leading-relaxed">
                            Your <strong className="text-gray-900">{topItems[0]?.name}</strong> is driving 20% of your orders. Consider running a "Best Seller" campaign to boost it further or cross-sell with <strong className="text-gray-900">{topItems[4]?.name || 'drinks'}</strong>.
                        </p>
                        <button
                            className="mt-4 text-xs bg-[#E23744] hover:bg-[#d12c39] text-white px-4 py-2 rounded-lg transition-all shadow-md shadow-red-500/20 active:scale-95"
                            onClick={() => router.push('/campaigns/new')}
                        >
                            Create Campaign Now
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
