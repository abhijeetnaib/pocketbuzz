'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import PosterEditor from '@/components/PosterEditor';
import { campaignApi, Campaign } from '@/lib/supabase';

function StudioContent() {
    const searchParams = useSearchParams();
    const campaignId = searchParams.get('campaign');

    const [campaign, setCampaign] = useState<Campaign | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [savedMessage, setSavedMessage] = useState('');

    useEffect(() => {
        async function loadCampaign() {
            if (!campaignId) {
                setIsLoading(false);
                return;
            }

            try {
                const data = await campaignApi.get(campaignId);
                setCampaign(data);
            } catch (err) {
                console.error('Failed to load campaign:', err);
            } finally {
                setIsLoading(false);
            }
        }

        loadCampaign();
    }, [campaignId]);

    const handleSave = async (data: { caption: string; imageUrl: string }) => {
        if (!campaign) return;

        setIsSaving(true);
        try {
            await campaignApi.approve(campaign.id, {
                modified_caption: data.caption,
                modified_image_url: data.imageUrl,
            });
            setSavedMessage('Changes saved!');
            setTimeout(() => {
                window.location.href = `/campaign/${campaign.id}`;
            }, 1000);
        } catch (err) {
            console.error('Failed to save:', err);
            setSavedMessage('Failed to save changes');
        } finally {
            setIsSaving(false);
        }
    };

    const handleCancel = () => {
        if (campaign) {
            window.location.href = `/campaign/${campaign.id}`;
        } else {
            window.location.href = '/';
        }
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center" style={{ minHeight: '100vh' }}>
                <div className="logo-icon mb-md">⚡</div>
                <p className="text-muted">Loading studio...</p>
            </div>
        );
    }

    if (!campaign) {
        return (
            <main>
                <header className="header">
                    <div className="logo">
                        <div className="logo-icon">⚡</div>
                        <span>Magic Studio</span>
                    </div>
                </header>

                <div className="text-center mt-2xl">
                    <h2 className="mb-md">No campaign selected</h2>
                    <p className="text-muted mb-lg">
                        Open a campaign from your notifications to edit it here.
                    </p>
                    <button
                        className="btn btn-primary"
                        onClick={() => window.location.href = '/'}
                    >
                        Go to Dashboard
                    </button>
                </div>
            </main>
        );
    }

    return (
        <main style={{ paddingBottom: '100px' }}>
            {/* Header */}
            <header className="header">
                <div className="logo">
                    <div className="logo-icon">✨</div>
                    <span>Magic Studio</span>
                </div>
                {isSaving && <span className="text-accent text-sm">Saving...</span>}
                {savedMessage && <span className="text-success text-sm">{savedMessage}</span>}
            </header>

            {/* Editor */}
            <PosterEditor
                imageUrl={campaign.generated_image_url}
                caption={campaign.generated_caption}
                onSave={handleSave}
                onCancel={handleCancel}
            />
        </main>
    );
}

export default function StudioPage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center" style={{ minHeight: '100vh' }}>
                <div className="logo-icon mb-md">⚡</div>
                <p className="text-muted">Loading studio...</p>
            </div>
        }>
            <StudioContent />
        </Suspense>
    );
}
