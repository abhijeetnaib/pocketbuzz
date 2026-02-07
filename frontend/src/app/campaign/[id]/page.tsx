'use client';

// ... (imports remain same)
import { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import CampaignCard from '@/components/CampaignCard';
import SwipeApproval from '@/components/SwipeApproval';
import { campaignApi, authApi, Campaign } from '@/lib/supabase';

export default function CampaignPage() {
    const params = useParams();
    const searchParams = useSearchParams();
    const campaignId = params.id as string;
    const token = searchParams.get('token');

    const [campaign, setCampaign] = useState<Campaign | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [restaurantName, setRestaurantName] = useState('');
    const [actionStatus, setActionStatus] = useState<'pending' | 'approved' | 'rejected' | 'sending' | 'sent'>('pending');

    // New states for regeneration
    const [isRegenerating, setIsRegenerating] = useState(false);
    const [showPromptInput, setShowPromptInput] = useState(false);
    const [manualPrompt, setManualPrompt] = useState('');

    useEffect(() => {
        async function loadData() {
            try {
                // Verify magic link token
                if (token) {
                    const authResult = await authApi.verify(token);
                    if (authResult.authenticated) {
                        setIsAuthenticated(true);
                        setRestaurantName(authResult.restaurant_name);
                    }
                } else {
                    setIsAuthenticated(true); // Allow direct access for testing
                }

                // Load campaign
                const campaignData = await campaignApi.get(campaignId);
                setCampaign(campaignData);
                setActionStatus(campaignData.status === 'PENDING' ? 'pending' :
                    campaignData.status === 'APPROVED' ? 'approved' :
                        campaignData.status === 'SENT' ? 'sent' : 'pending');
            } catch (err) {
                setError('Could not load campaign');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        }

        loadData();
    }, [campaignId, token]);

    const handleApprove = async () => {
        if (!campaign) return;

        try {
            setActionStatus('approved');
            await campaignApi.approve(campaign.id);

            // Auto-send after approval
            setActionStatus('sending');
            await campaignApi.send(campaign.id);
            setActionStatus('sent');
        } catch (err) {
            setError('Failed to send campaign');
            setActionStatus('pending');
        }
    };

    const handleReject = async () => {
        if (!campaign) return;

        try {
            setActionStatus('rejected');
            await campaignApi.reject(campaign.id);
        } catch (err) {
            setError('Failed to reject campaign');
            setActionStatus('pending');
        }
    };

    const handleEdit = () => {
        window.location.href = `/studio?campaign=${campaignId}`;
    };

    const handleRegenerate = async () => {
        if (!campaign) return;
        setIsRegenerating(true);
        try {
            const result = await campaignApi.regenerateImage(campaign.id, manualPrompt || undefined);

            // Update local state with new image
            setCampaign({
                ...campaign,
                generated_image_url: result.image_url
            });
            setShowPromptInput(false); // Hide input after success
        } catch (err) {
            console.error(err);
            setError('Failed to regenerate image');
        } finally {
            setIsRegenerating(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
                <div className="w-16 h-16 border-4 border-[#E23744] border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-gray-500 font-medium">Loading campaign...</p>
            </div>
        );
    }

    if (error || !campaign) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-center p-4">
                <h2 className="text-2xl font-bold mb-4 text-gray-900">😕 Oops!</h2>
                <p className="text-gray-500 mb-8">{error || 'Campaign not found'}</p>
                <button
                    className="bg-[#E23744] text-white px-6 py-2 rounded-lg font-semibold hover:bg-[#d12c39] transition-colors shadow-lg shadow-red-500/20"
                    onClick={() => window.location.href = '/'}
                >
                    Go Home
                </button>
            </div>
        );
    }

    return (
        <main className="animate-slide-up pb-20 px-4 pt-6 max-w-md mx-auto min-h-screen bg-gray-50">
            {/* Header */}
            <header className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-[#E23744] to-[#c21f2d] rounded-full flex items-center justify-center font-bold text-white shadow-md shadow-red-500/20">⚡</div>
                    <span className="font-bold text-gray-900 text-lg">PocketBuzz</span>
                </div>
                {restaurantName && (
                    <span className="text-gray-500 text-sm font-medium bg-white px-2 py-1 rounded-md border border-gray-100 shadow-sm">{restaurantName}</span>
                )}
            </header>

            {/* Insight Banner */}
            <div className="bg-orange-50 border border-orange-100 p-4 rounded-xl mb-6 shadow-sm">
                <p className="text-orange-700 text-sm font-medium flex gap-2">
                    <span>💡</span> {campaign.insight_text}
                </p>
            </div>

            {/* Campaign Preview */}
            <div className="relative">
                {isRegenerating && (
                    <div className="absolute inset-0 z-50 bg-white/90 flex flex-col items-center justify-center rounded-xl backdrop-blur-sm border border-gray-100">
                        <div className="w-10 h-10 border-4 border-[#E23744] border-t-transparent rounded-full animate-spin mb-4"></div>
                        <p className="text-gray-900 font-bold">Cooking up a new image...</p>
                    </div>
                )}

                {actionStatus === 'pending' ? (
                    <SwipeApproval
                        onSwipeRight={handleApprove}
                        onSwipeLeft={handleReject}
                    >
                        <CampaignCard
                            imageUrl={campaign.generated_image_url}
                            caption={campaign.generated_caption}
                            status={campaign.status}
                        />
                    </SwipeApproval>
                ) : (
                    <CampaignCard
                        imageUrl={campaign.generated_image_url}
                        caption={campaign.generated_caption}
                        status={
                            actionStatus === 'approved' ? 'APPROVED' :
                                actionStatus === 'sending' ? 'APPROVED' :
                                    actionStatus === 'sent' ? 'SENT' :
                                        actionStatus === 'rejected' ? 'FAILED' : campaign.status
                        }
                    />
                )}
            </div>

            {/* Regeneration Controls */}
            {actionStatus === 'pending' && !isRegenerating && (
                <div className="mt-6 animate-fade-in">
                    {!showPromptInput ? (
                        <button
                            className="text-sm text-gray-500 flex items-center gap-2 mx-auto hover:text-[#E23744] transition-colors font-medium"
                            onClick={() => setShowPromptInput(true)}
                        >
                            🔄 Regenerate Image
                        </button>
                    ) : (
                        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                            <label className="text-xs text-gray-500 font-bold uppercase tracking-wider mb-2 block">Describe the image you want:</label>
                            <textarea
                                className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-900 focus:outline-none focus:border-[#E23744] transition-colors mb-3 placeholder-gray-400"
                                rows={3}
                                placeholder="E.g. Spicy red chicken curry in a copper bowl with naan on the side..."
                                value={manualPrompt}
                                onChange={(e) => setManualPrompt(e.target.value)}
                            />
                            <div className="flex gap-2">
                                <button
                                    className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 rounded-lg text-sm transition-colors font-medium"
                                    onClick={() => setShowPromptInput(false)}
                                >
                                    Cancel
                                </button>
                                <button
                                    className="flex-1 bg-[#E23744] hover:bg-[#d12c39] text-white py-2 rounded-lg text-sm transition-colors font-bold shadow-md shadow-red-500/20"
                                    onClick={handleRegenerate}
                                >
                                    ✨ Generate
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Status Messages */}
            {actionStatus === 'sending' && (
                <div className="text-center mt-8 animate-fade-in">
                    <div className="text-4xl mb-2 animate-bounce"></div>
                    <p className="text-[#E23744] font-medium">Sending to your customers...</p>
                </div>
            )}

            {actionStatus === 'sent' && (
                <div className="text-center mt-8 animate-fade-in">
                    <div className="text-4xl mb-2">✅</div>
                    <h3 className="text-green-600 text-xl font-bold mb-2">Campaign Sent!</h3>
                    <p className="text-gray-500">Your customers will receive it shortly.</p>
                </div>
            )}

            {actionStatus === 'rejected' && (
                <div className="text-center mt-8 animate-fade-in">
                    <div className="text-4xl mb-2">🗑️</div>
                    <p className="text-gray-500">Campaign dismissed</p>
                </div>
            )}

            {/* Action Buttons */}
            {actionStatus === 'pending' && (
                <div className="flex flex-col gap-3 mt-8">
                    <button
                        className="w-full bg-[#E23744] hover:bg-[#d12c39] text-white py-3.5 rounded-xl font-bold shadow-lg shadow-red-500/20 transition-all active:scale-95 transform hover:-translate-y-1"
                        onClick={handleApprove}
                    >
                        ✓ Approve & Send
                    </button>
                    <button
                        className="w-full bg-white hover:bg-gray-50 text-gray-700 py-3.5 rounded-xl font-bold border border-gray-200 shadow-sm transition-all active:scale-95"
                        onClick={handleEdit}
                    >
                        ✏️ Edit in Studio
                    </button>
                    <button
                        className="w-full text-gray-400 hover:text-gray-600 py-2 text-sm transition-colors font-medium"
                        onClick={handleReject}
                    >
                        Skip this campaign
                    </button>
                </div>
            )}

            {actionStatus === 'sent' && (
                <div className="mt-8">
                    <button
                        className="w-full bg-white hover:bg-gray-50 text-gray-900 py-3.5 rounded-xl font-bold border border-gray-200 shadow-sm transition-all"
                        onClick={() => window.location.href = '/'}
                    >
                        ← Back to Dashboard
                    </button>
                </div>
            )}
        </main>
    );
}
