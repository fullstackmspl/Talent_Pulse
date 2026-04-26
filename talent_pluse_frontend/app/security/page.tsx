'use client';

import { motion } from 'framer-motion';
import { Shield, Lock, EyeOff, ShieldCheck, Key, ArrowLeft, Fingerprint, Activity } from 'lucide-react';
import Link from 'next/link';
import Logo from '../Logo';

export default function SecurityPage() {
    return (
        <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] selection:bg-cyan-500/30">
            {/* Background with Grid Pattern */}
            <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.03]"
                style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute top-[30%] left-[10%] w-[400px] h-[400px] bg-red-500/5 blur-[100px] rounded-full" />
                <div className="absolute top-[10%] right-[10%] w-[500px] h-[500px] bg-cyan-600/5 blur-[100px] rounded-full" />
            </div>

            <nav className="relative z-50 flex items-center justify-between px-6 py-8 max-w-7xl mx-auto">
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="p-2 rounded-xl bg-black/5 group-hover:bg-cyan-500 group-hover:text-white transition-all">
                        <ArrowLeft size={18} />
                    </div>
                    <Logo size={32} />
                    <h1 className="text-xl font-black tracking-tighter italic uppercase">
                        TALENT<span className="text-cyan-500">PULSE</span>
                    </h1>
                </Link>
            </nav>

            <main className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-40">
                <div className="grid lg:grid-cols-2 gap-20 items-center mb-40">
                    <motion.div
                        initial={{ opacity: 0, x: -50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                    >
                        <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-red-500/10 border border-red-500/20 mb-6 font-black uppercase text-[10px] text-red-600 tracking-widest">
                            <Shield size={12} /> Military Grade Defense
                        </div>
                        <h2 className="text-5xl md:text-7xl font-black tracking-tighter italic uppercase mb-8 leading-tight">
                            DATA <span className="text-red-500">FORTRESS</span> ENCRYPTION
                        </h2>
                        <p className="text-[var(--text-muted)] text-lg leading-relaxed mb-10">
                            Your business data is your most valuable asset. TalentPulse employs a decentralized zero-trust architecture, ensuring that every query and record is encrypted with AES-256 protocols.
                        </p>
                        <ul className="space-y-6">
                            {[
                                { icon: <Lock size={18} />, text: "End-to-End Vector Encryption" },
                                { icon: <EyeOff size={18} />, text: "Zero-Knowledge Storage Policy" },
                                { icon: <Fingerprint size={18} />, text: "Multi-Factor Identity Validation" }
                            ].map((item, i) => (
                                <li key={i} className="flex items-center gap-4 text-xs font-black uppercase tracking-widest text-cyan-600">
                                    <span className="p-2 rounded-lg bg-cyan-500/10">{item.icon}</span>
                                    {item.text}
                                </li>
                            ))}
                        </ul>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        className="relative"
                    >
                        <div className="aspect-square rounded-[4rem] bg-gradient-to-tr from-black to-slate-900 shadow-2xl p-1 items-center justify-center flex relative group">
                            <div className="absolute inset-0 bg-red-500/20 blur-[80px] rounded-full group-hover:bg-cyan-500/30 transition-all duration-1000" />
                            <div className="w-full h-full rounded-[3.8rem] bg-slate-900 border border-white/5 flex flex-col items-center justify-center relative overflow-hidden">
                                <ShieldCheck size={120} className="text-cyan-500 animate-pulse mb-8" />
                                <div className="flex flex-col items-center gap-3">
                                    <div className="h-1 w-32 bg-white/10 rounded-full overflow-hidden">
                                        <motion.div
                                            animate={{ x: [-128, 128] }}
                                            transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                                            className="h-full w-full bg-cyan-500" />
                                    </div>
                                    <span className="text-[10px] font-black uppercase tracking-[0.5em] text-cyan-500/60">Scanning Protocols</span>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    {[
                        { title: "Sovereignty", value: "100%", desc: "Data ownership remained" },
                        { title: "Uptime", value: "99.9%", desc: "System availability" },
                        { title: "Hashing", value: "SHA-3", desc: "Integrity validation" },
                        { title: "Compliance", value: "SOC-2", desc: "Industry standard" }
                    ].map((stat, i) => (
                        <div key={i} className="p-8 rounded-3xl bg-[var(--card-bg)] border border-[var(--border-color)] text-center">
                            <p className="text-3xl font-black italic uppercase mb-1">{stat.value}</p>
                            <p className="text-[10px] font-black uppercase tracking-widest text-cyan-500 mb-2">{stat.title}</p>
                            <p className="text-[var(--text-muted)] text-[10px]">{stat.desc}</p>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}
