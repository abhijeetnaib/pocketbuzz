'use client';

import { useRef, useState, ReactNode } from 'react';
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion';

interface SwipeApprovalProps {
    children: ReactNode;
    onSwipeRight: () => void;
    onSwipeLeft: () => void;
    threshold?: number;
}

export default function SwipeApproval({
    children,
    onSwipeRight,
    onSwipeLeft,
    threshold = 100,
}: SwipeApprovalProps) {
    const [isDragging, setIsDragging] = useState(false);
    const x = useMotionValue(0);

    // Rotate slightly based on drag
    const rotate = useTransform(x, [-200, 0, 200], [-10, 0, 10]);

    // Background color hints
    const leftOpacity = useTransform(x, [-threshold, 0], [1, 0]);
    const rightOpacity = useTransform(x, [0, threshold], [0, 1]);

    const handleDragEnd = (_: any, info: PanInfo) => {
        const offset = info.offset.x;
        const velocity = info.velocity.x;

        if (offset > threshold || velocity > 500) {
            onSwipeRight();
        } else if (offset < -threshold || velocity < -500) {
            onSwipeLeft();
        }
        setIsDragging(false);
    };

    return (
        <div className="swipe-container">
            {/* Background hints */}
            <motion.div
                style={{
                    position: 'absolute',
                    inset: 0,
                    background: 'linear-gradient(90deg, rgba(239, 68, 68, 0.2), transparent)',
                    opacity: leftOpacity,
                    borderRadius: 'var(--radius-xl)',
                    zIndex: 0,
                }}
            />
            <motion.div
                style={{
                    position: 'absolute',
                    inset: 0,
                    background: 'linear-gradient(-90deg, rgba(52, 211, 153, 0.2), transparent)',
                    opacity: rightOpacity,
                    borderRadius: 'var(--radius-xl)',
                    zIndex: 0,
                }}
            />

            {/* Draggable card */}
            <motion.div
                drag="x"
                dragConstraints={{ left: 0, right: 0 }}
                dragElastic={0.7}
                onDragStart={() => setIsDragging(true)}
                onDragEnd={handleDragEnd}
                style={{ x, rotate, position: 'relative', zIndex: 1 }}
                whileTap={{ cursor: 'grabbing' }}
            >
                {children}
            </motion.div>

            {/* Swipe hints */}
            <div className="swipe-hint">
                <span className="swipe-hint-left">← Swipe to skip</span>
                <span className="swipe-hint-right">Swipe to approve →</span>
            </div>
        </div>
    );
}
