'use client';

import { motion } from 'framer-motion';

interface LogoProps {
    className?: string;
    size?: number;
}

export default function Logo({ className = "", size = 40 }: LogoProps) {
    return (
        <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className={`relative flex items-center justify-center ${className}`}
            style={{ width: size, height: size }}
        >
            <svg
                viewBox="0 0 100 100"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="w-full h-full drop-shadow-2xl"
            >
                <defs>
                    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#0ea5e9" />
                        <stop offset="100%" stopColor="#2563eb" />
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>

                {/* Abstract Pulse Path */}
                <motion.path
                    d="M10 50 L25 50 L35 25 L45 75 L55 50 L90 50"
                    stroke="url(#logoGradient)"
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                />

                {/* Neural Nodes */}
                <circle cx="25" cy="50" r="3" fill="#0ea5e9" opacity="0.6" />
                <circle cx="35" cy="25" r="3" fill="#0ea5e9" />
                <circle cx="45" cy="75" r="3" fill="#2563eb" />
                <circle cx="55" cy="50" r="3" fill="#2563eb" opacity="0.6" />

                {/* Background Glow */}
                <circle cx="50" cy="50" r="40" stroke="url(#logoGradient)" strokeWidth="1" strokeDasharray="4 4" opacity="0.2">
                    <animateTransform
                        attributeName="transform"
                        type="rotate"
                        from="0 50 50"
                        to="360 50 50"
                        dur="10s"
                        repeatCount="indefinite"
                    />
                </circle>
            </svg>
        </motion.div>
    );
}
