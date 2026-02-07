'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { campaignApi } from '@/lib/supabase';

export default function NewCampaignPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState<any[]>([]);
    const [loadingSuggestions, setLoadingSuggestions] = useState(true);
    const [formData, setFormData] = useState({
        item_name: '',
        topic: '',
    });

    useEffect(() => {
        // Fetch AI suggestions on load
        const loadSuggestions = async () => {
            const restaurantId = localStorage.getItem('pb_restaurant_id');
            if (!restaurantId) return;

            try {
                const data = await campaignApi.getSuggestions(restaurantId);
                setSuggestions(data);
            } catch (err) {
                console.error("Failed to load suggestions", err);
            } finally {
                setLoadingSuggestions(false);
            }
        };

        loadSuggestions();
    }, []);

    const handleCreate = async (item: string, topic: string, strategy: string = 'BEST_SELLER') => {
        setLoading(true);
        const restaurantId = localStorage.getItem('pb_restaurant_id');

        if (!restaurantId) {
            router.push('/login');
            return;
        }

        try {
            const newCampaign = await campaignApi.create({
                restaurant_id: restaurantId,
                strategy_type: strategy,
                item_name: item,
                insight_text: topic,
            });

            if (newCampaign?.id) {
                router.push(`/campaign/${newCampaign.id}`);
            }
        } catch (err: any) {
            console.error(err);
            const errorMsg = err.message || 'Unknown error';
            alert(`Failed to create campaign: ${errorMsg}`);
            setLoading(false);
        }
    };

    const handleManualSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        handleCreate(formData.item_name, formData.topic || `Promoting ${formData.item_name}`, 'CUSTOM');
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
                <div className="w-16 h-16 border-4 border-[#E23744] border-t-transparent rounded-full animate-spin mb-4"></div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Cooking up Magic ⚡</h2>
                <p className="text-gray-500">AI is generating your campaign copy & visuals...</p>
            </div>
        );
    }

    return (
        <div className="animate-slide-up max-w-2xl mx-auto pb-20">
            {/* Header */}
            <div className="flex items-center gap-4 mb-8">
                <button
                    onClick={() => router.back()}
                    className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-900 transition-colors"
                >
                    ←
                </button>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">New Campaign</h1>
                    <p className="text-gray-500 text-sm">Create a marketing blast in seconds</p>
                </div>
            </div>

            {/* AI Suggestions Section */}
            <section className="mb-10">
                <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    ✨ AI Suggestions <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-normal">Based on your sales</span>
                </h2>

                {loadingSuggestions ? (
                    <div className="grid md:grid-cols-2 gap-4">
                        {[1, 2].map(i => (
                            <div key={i} className="h-40 bg-gray-100 animate-pulse rounded-xl border border-gray-200"></div>
                        ))}
                    </div>
                ) : suggestions.length > 0 ? (
                    <div className="grid md:grid-cols-2 gap-4">
                        {suggestions.map((suggestion, idx) => (
                            <div
                                key={idx}
                                onClick={() => handleCreate(suggestion.item_name || 'Special Item', suggestion.insight_text, suggestion.strategy_type)}
                                className="group relative bg-white border border-gray-100 p-4 md:p-5 rounded-xl hover:border-red-200 hover:shadow-md transition-all cursor-pointer overflow-hidden shadow-sm active:scale-[0.98]"
                            >
                                <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-[#E23744] to-[#c21f2d] opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                <div className="mb-2 md:mb-3">
                                    <span className="text-[10px] font-mono uppercase tracking-wider bg-gray-100 text-gray-600 px-2 py-1 rounded-md border border-gray-200">
                                        {suggestion.strategy_type.replace('_', ' ')}
                                    </span>
                                </div>
                                <p className="text-gray-600 text-sm mb-3 md:mb-4 line-clamp-3 group-hover:text-gray-900">
                                    {suggestion.insight_text}
                                </p>
                                <div className="flex items-center text-[#E23744] text-xs font-bold group-hover:gap-2 transition-all">
                                    Launch This Campaign <span>→</span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="bg-white border border-gray-100 p-6 rounded-xl text-center shadow-sm">
                        <p className="text-gray-500 text-sm">
                            Not enough data for suggestions yet. Try creating a manual campaign!
                        </p>
                    </div>
                )}
            </section>

            {/* Divider */}
            <div className="relative flex items-center gap-4 mb-8 md:mb-10">
                <div className="h-px bg-gray-200 flex-1"></div>
                <span className="text-gray-400 text-[10px] md:text-xs uppercase font-medium">Or Create Manual</span>
                <div className="h-px bg-gray-200 flex-1"></div>
            </div>

            {/* Manual Form */}
            <div className="bg-white border border-gray-100 p-5 md:p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                <form onSubmit={handleManualSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">
                            What item do you want to promote?
                        </label>
                        <input
                            type="text"
                            required
                            placeholder="e.g. Butter Chicken, Weekend Thali..."
                            className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#E23744] focus:ring-1 focus:ring-[#E23744]/20 transition-all"
                            value={formData.item_name}
                            onChange={(e) => setFormData({ ...formData, item_name: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">
                            Any specific message or offer? (Optional)
                        </label>
                        <textarea
                            rows={3}
                            placeholder="e.g. Flat 20% off for weekend..."
                            className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#E23744] focus:ring-1 focus:ring-[#E23744]/20 transition-all"
                            value={formData.topic}
                            onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                        />
                    </div>

                    <div className="pt-2">
                        <button
                            type="submit"
                            className="w-full bg-[#E23744] hover:bg-[#d12c39] text-white font-bold py-4 rounded-xl shadow-lg shadow-red-500/20 transition-all hover:-translate-y-1 active:scale-[0.98]"
                        >
                            Create Custom Campaign
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
