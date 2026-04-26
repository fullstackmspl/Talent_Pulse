'use client';

import { motion } from 'framer-motion';
import { Database, Zap, Cpu, Server, Globe, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import Logo from '../Logo';

export default function InfrastructurePage() {
    return (
        <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] selection:bg-cyan-500/30">
            {/* Background */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute top-[20%] left-[-10%] w-[500px] h-[500px] bg-cyan-500/5 blur-[120px] rounded-full" />
                <div className="absolute bottom-[20%] right-[-10%] w-[500px] h-[500px] bg-blue-600/5 blur-[120px] rounded-full" />
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
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-32"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 mb-6">
                        <Server size={12} className="text-cyan-600" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-cyan-700">System Architecture</span>
                    </div>
                    <h2 className="text-5xl md:text-7xl font-black tracking-tighter italic uppercase mb-8">
                        QUANTUM <span className="text-cyan-500">INFRASTRUCTURE</span>
                    </h2>
                    <p className="max-w-3xl mx-auto text-[var(--text-muted)] text-lg leading-relaxed">
                        Our infrastructure is built on a zero-latency neural backbone, designed to process and index complex business intelligence data in real-time.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-32">
                    {[
                        {
                            icon: <Database />,
                            title: "Vector Storage",
                            desc: "High-performance Qdrant vector database optimized for multi-dimensional business records and similarity search.",
                            color: "bg-blue-500/10 text-blue-500"
                        },
                        {
                            icon: <Zap />,
                            title: "Neural Ingestion",
                            desc: "Automated ETL pipeline using Gemini-3 to structure raw documents into queryable intelligence chunks.",
                            color: "bg-yellow-500/10 text-yellow-500"
                        },
                        {
                            icon: <Cpu />,
                            title: "Compute Fabric",
                            desc: "Scalable backend processing environment capable of handling thousands of concurrent analytical requests.",
                            color: "bg-purple-500/10 text-purple-500"
                        },
                        {
                            icon: <Globe />,
                            title: "Edge Access",
                            desc: "Distributed access nodes ensuring sub-hundred millisecond response times globally for business operations.",
                            color: "bg-green-500/10 text-green-500"
                        }
                    ].map((item, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            className="p-12 rounded-[3rem] bg-[var(--card-bg)] border border-[var(--border-color)] shadow-xl group hover:border-cyan-500 transition-all"
                        >
                            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-8 ${item.color} group-hover:scale-110 transition-transform`}>
                                {item.icon}
                            </div>
                            <h3 className="text-2xl font-black italic uppercase mb-4">{item.title}</h3>
                            <p className="text-[var(--text-muted)] leading-relaxed">{item.desc}</p>
                        </motion.div>
                    ))}
                </div>

                <section className="p-16 rounded-[4rem] bg-black text-white relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-full h-full opacity-20 pointer-events-none">
                        <div className="absolute top-[-50%] right-[-20%] w-[1000px] h-[1000px] bg-cyan-500 blur-[200px] rounded-full" />
                    </div>
                    <div className="relative z-10 grid md:grid-cols-2 items-center gap-16">
                        <div>
                            <h2 className="text-4xl font-black tracking-tighter italic uppercase mb-6 leading-tight">
                                BUILT FOR <span className="text-cyan-400">MISSION CRITICAL</span> OPERATIONS
                            </h2>
                            <p className="text-gray-400 leading-relaxed mb-10">
                                TalentPulse is not just a chatbot; it's a mission-command center for your business data. Our infrastructure guarantees 99.99% uptime for mission-critical protocols.
                            </p>
                            <Link href="/dashboard" className="px-8 py-4 bg-cyan-500 rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-cyan-400 transition-all inline-block">
                                Explore Dashboard
                            </Link>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="aspect-square rounded-3xl border border-white/10 bg-white/5 flex flex-col items-center justify-center text-center p-6">
                                <span className="text-4xl font-black text-cyan-400 mb-2">0.5s</span>
                                <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Latency</span>
                            </div>
                            <div className="aspect-square rounded-3xl border border-white/10 bg-white/5 flex flex-col items-center justify-center text-center p-6 mt-8">
                                <span className="text-4xl font-black text-cyan-400 mb-2">1M+</span>
                                <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Nodes</span>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}
