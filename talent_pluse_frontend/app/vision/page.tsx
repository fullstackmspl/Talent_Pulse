'use client';

import { motion } from 'framer-motion';
import { Eye, Target, Compass, Sparkles, ArrowLeft, Lightbulb } from 'lucide-react';
import Link from 'next/link';
import Logo from '../Logo';

export default function VisionPage() {
    return (
        <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] selection:bg-cyan-500/30">
            {/* Background */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute top-[10%] right-[-5%] w-[600px] h-[600px] bg-blue-500/5 blur-[150px] rounded-full" />
                <div className="absolute bottom-[10%] left-[-5%] w-[600px] h-[600px] bg-cyan-600/5 blur-[150px] rounded-full" />
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

            <main className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-40 text-center">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mb-32"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
                        <Eye size={12} className="text-blue-600" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-blue-700">Future Horizon</span>
                    </div>
                    <h2 className="text-6xl md:text-9xl font-black tracking-tighter italic uppercase mb-12">
                        THE <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-600">VISION</span> 2030
                    </h2>
                    <p className="max-w-4xl mx-auto text-[var(--text-muted)] text-xl font-medium leading-relaxed">
                        We are redefining how humanity interacts with corporate data. Our vision is to create a seamless synergy between human intuition and machine intelligence, turning every data point into an actionable breakthrough.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-40">
                    {[
                        {
                            icon: <Target className="w-8 h-8" />,
                            title: "Precision Analytics",
                            desc: "Eliminating guesswork by providing hyper-accurate predictions based on historical data trends."
                        },
                        {
                            icon: <Lightbulb className="w-8 h-8" />,
                            title: "Autonomous Insight",
                            desc: "A system that doesn't just answer questions but proactively alerts you to business opportunities."
                        },
                        {
                            icon: <Compass className="w-8 h-8" />,
                            title: "Ethical AI",
                            desc: "Building intelligence that respects privacy, ensures data sovereignty, and operates with full transparency."
                        }
                    ].map((item, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            viewport={{ once: true }}
                            className="group"
                        >
                            <div className="mb-8 mx-auto w-24 h-24 rounded-[2rem] bg-white border border-[var(--border-color)] shadow-xl flex items-center justify-center text-cyan-500 group-hover:bg-gradient-to-tr group-hover:from-cyan-500 group-hover:to-blue-600 group-hover:text-white group-hover:scale-110 transition-all duration-500">
                                {item.icon}
                            </div>
                            <h3 className="text-xl font-black italic uppercase mb-4 tracking-tight">{item.title}</h3>
                            <p className="text-[var(--text-muted)] text-sm leading-relaxed">{item.desc}</p>
                        </motion.div>
                    ))}
                </div>

                <section className="relative py-20">
                    <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/5 to-blue-600/5 rounded-[5rem] -z-10" />
                    <h2 className="text-3xl font-black uppercase italic mb-16">Global Impact Core</h2>
                    <div className="flex flex-wrap justify-center gap-12">
                        {[1, 2, 3, 4].map(i => (
                            <div key={i} className="flex flex-col items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-cyan-500 animate-ping" />
                                <span className="text-[10px] font-black uppercase tracking-widest opacity-40">Node {i}02-B</span>
                            </div>
                        ))}
                    </div>
                </section>
            </main>
        </div>
    );
}
