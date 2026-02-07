'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';

interface PosterEditorProps {
    imageUrl: string;
    caption: string;
    onSave: (data: { caption: string; imageUrl: string }) => void;
    onCancel: () => void;
}

export default function PosterEditor({
    imageUrl,
    caption: initialCaption,
    onSave,
    onCancel,
}: PosterEditorProps) {
    const [caption, setCaption] = useState(initialCaption);
    const [isGeneratingImage, setIsGeneratingImage] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [caption]);

    const handleSave = () => {
        onSave({ caption, imageUrl });
    };

    const regenerateImage = async () => {
        setIsGeneratingImage(true);
        // TODO: Call AI engine to regenerate
        setTimeout(() => setIsGeneratingImage(false), 2000);
    };

    return (
        <div className="animate-slide-up">
            {/* Preview */}
            <div className="card mb-lg">
                <div style={{ position: 'relative', aspectRatio: '1' }}>
                    <Image
                        src={imageUrl}
                        alt="Campaign poster"
                        fill
                        style={{ objectFit: 'cover' }}
                    />
                    {isGeneratingImage && (
                        <div
                            className="flex items-center justify-center"
                            style={{
                                position: 'absolute',
                                inset: 0,
                                background: 'rgba(10, 10, 11, 0.8)',
                            }}
                        >
                            <div className="text-center">
                                <div className="mb-sm">✨</div>
                                <p className="text-accent">Generating new image...</p>
                            </div>
                        </div>
                    )}
                </div>
                <div className="card-content">
                    <button
                        className="btn btn-secondary btn-block"
                        onClick={regenerateImage}
                        disabled={isGeneratingImage}
                    >
                        🎨 Regenerate Image
                    </button>
                </div>
            </div>

            {/* Caption Editor */}
            <div className="mb-lg">
                <label className="text-muted text-sm mb-sm" style={{ display: 'block' }}>
                    Edit Caption
                </label>
                <textarea
                    ref={textareaRef}
                    value={caption}
                    onChange={(e) => setCaption(e.target.value)}
                    placeholder="Write your marketing message..."
                    style={{
                        minHeight: '100px',
                        resize: 'none',
                    }}
                />
                <p className="text-muted text-sm mt-xs">
                    {caption.length}/280 characters
                </p>
            </div>

            {/* Quick Suggestions */}
            <div className="mb-xl">
                <p className="text-muted text-sm mb-sm">Quick add:</p>
                <div className="flex gap-sm" style={{ flexWrap: 'wrap' }}>
                    {['🔥', '😋', '🎉', '💯', '👉'].map((emoji) => (
                        <button
                            key={emoji}
                            className="btn btn-ghost"
                            style={{ padding: 'var(--spacing-sm)' }}
                            onClick={() => setCaption(caption + ' ' + emoji)}
                        >
                            {emoji}
                        </button>
                    ))}
                </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col gap-sm">
                <button className="btn btn-primary btn-block" onClick={handleSave}>
                    ✓ Save & Preview
                </button>
                <button className="btn btn-ghost btn-block" onClick={onCancel}>
                    Cancel
                </button>
            </div>
        </div>
    );
}
