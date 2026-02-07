'use client';

import { useState } from 'react';
import Image from 'next/image';

interface CampaignCardProps {
    imageUrl: string;
    caption: string;
    status: 'PENDING' | 'APPROVED' | 'SENT' | 'FAILED';
}

export default function CampaignCard({ imageUrl, caption, status }: CampaignCardProps) {
    const [imageError, setImageError] = useState(false);

    const statusConfig = {
        PENDING: { label: 'Ready to Send', className: 'badge-pending' },
        APPROVED: { label: 'Approved', className: 'badge-approved' },
        SENT: { label: 'Sent', className: 'badge-sent' },
        FAILED: { label: 'Dismissed', className: '' },
    };

    const { label, className } = statusConfig[status] || statusConfig.PENDING;

    return (
        <div className="campaign-card animate-fade-in">
            {/* Status Badge */}
            <div style={{
                position: 'absolute',
                top: 'var(--spacing-md)',
                right: 'var(--spacing-md)',
                zIndex: 10
            }}>
                <span className={`badge ${className}`}>{label}</span>
            </div>

            {/* Campaign Poster */}
            <div style={{ position: 'relative', width: '100%', aspectRatio: '1' }}>
                {!imageError ? (
                    <Image
                        src={imageUrl}
                        alt="Campaign poster"
                        fill
                        style={{ objectFit: 'cover' }}
                        onError={() => setImageError(true)}
                        priority
                    />
                ) : (
                    <div
                        className="flex items-center justify-center"
                        style={{
                            width: '100%',
                            height: '100%',
                            background: 'var(--bg-secondary)'
                        }}
                    >
                        <span className="text-muted">🖼️ Image unavailable</span>
                    </div>
                )}
            </div>

            {/* Caption */}
            <div className="campaign-caption">
                <p style={{ whiteSpace: 'pre-wrap' }}>{caption}</p>
            </div>
        </div>
    );
}
