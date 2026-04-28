'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ArrowRight, Shield, Zap, BarChart3, Globe, User, Settings, Loader2, Play, MousePointer2, Layers, Binary, Workflow, Database, Eye } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Logo from './Logo';

export default function LandingPage() {
  const router = useRouter();
  const [showLogin, setShowLogin] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Join Us Form State
  const [showJoinUs, setShowJoinUs] = useState(false);
  const [leadForm, setLeadForm] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    service: '',
    budget: '50000',
    message: ''
  });
  const [leadLoading, setLeadLoading] = useState(false);
  const [leadSuccess, setLeadSuccess] = useState('');
  const [leadError, setLeadError] = useState('');

  const handleLeadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLeadLoading(true);
    setLeadError('');
    setLeadSuccess('');
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'https://talentpulse.meander.one/api';
      const res = await axios.post(`${apiBase}/public/lead`, leadForm);
      if (res.data.status === 'success') {
        setLeadSuccess('Thank you! Your request has been submitted successfully.');
        setLeadForm({ name: '', email: '', phone: '', company: '', service: '', budget: '50000', message: '' });
        setTimeout(() => { setShowJoinUs(false); setLeadSuccess(''); }, 3000);
      } else {
        setLeadError(res.data.message || 'Failed to submit form.');
      }
    } catch (err: any) {
      setLeadError(err.response?.data?.detail || 'Failed to submit request.');
    }
    setLeadLoading(false);
  };

  useEffect(() => {
    if (localStorage.getItem('genius_auth') === 'true') {
      router.push('/dashboard');
    }
  }, [router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'https://talentpulse.meander.one/api';
      const res = await axios.post(`${apiBase}/login`, {
        email,
        password
      });

      if (res.data.status === 'success') {
        localStorage.setItem('genius_auth', 'true');
        localStorage.setItem('talent_pulse_token', res.data.data.access_token);
        router.push('/dashboard');
      } else {
        setError(res.data.message || 'Login failed');
        setLoading(false);
      }
    } catch (err: any) {
      console.error('Login Error:', err);
      setError(err.response?.data?.detail || 'Unauthorized access. Check credentials.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] overflow-x-hidden selection:bg-cyan-500/30">

      {/* Background Decor */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] w-[800px] h-[800px] bg-cyan-500/5 blur-[180px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[800px] h-[800px] bg-blue-600/5 blur-[180px] rounded-full" />
      </div>

      {/* Modern Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-[100] bg-white/70 backdrop-blur-2xl border-b border-[var(--border-color)]">
        <div className="flex items-center justify-between px-6 lg:px-12 py-5 max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <Logo size={36} className="scale-110" />
            <span className="text-xl font-black tracking-tighter italic uppercase hidden sm:block">
              TALENT<span className="text-cyan-500">PULSE</span>
            </span>
          </div>

          <div className="hidden md:flex items-center gap-12 text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">
            <Link href="/infrastructure" className="hover:text-cyan-500 transition-all hover:translate-y-[-1px]">Infrastructure</Link>
            <Link href="/vision" className="hover:text-cyan-500 transition-all hover:translate-y-[-1px]">Vision</Link>
            <Link href="/security" className="hover:text-cyan-500 transition-all hover:translate-y-[-1px]">Security</Link>
          </div>

          <button
            onClick={() => setShowLogin(true)}
            className="group px-8 py-3 rounded-2xl bg-black text-white text-[10px] font-black uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-xl shadow-black/10 flex items-center gap-2"
          >
            Access Portal <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-32 md:pt-44 pb-20 md:pb-32 px-4 sm:px-6 max-w-7xl mx-auto text-center">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
          <div className="inline-flex items-center gap-2 px-4 sm:px-6 py-2 rounded-full bg-cyan-500/5 border border-cyan-500/10 mb-6 sm:mb-8">
            <Sparkles size={14} className="text-cyan-600" />
            <span className="text-[9px] sm:text-[10px] font-black uppercase tracking-[0.2em] sm:tracking-[0.4em] text-cyan-600">Enterprise AI Orchestration</span>
          </div>

          <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl 2xl:text-9xl font-black tracking-tighter leading-[1.1] sm:leading-[0.95] italic uppercase mb-6 sm:mb-10 px-2">
            <span className="block sm:inline">THE PULSE OF</span>{' '}
            <span className="block mt-2 sm:mt-0 text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-600">INTELLIGENT</span>{' '}
            <span className="block sm:inline mt-2 sm:mt-0">DATA</span>
          </h2>

          <p className="max-w-2xl mx-auto text-[var(--text-muted)] text-base sm:text-lg md:text-xl font-medium leading-relaxed mb-10 sm:mb-16 opacity-80 px-4">
            Unlock the hidden potential of your business operations. TalentPulse doesn't just process data—it orchestrates it into a strategic weapon for business growth.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 mb-12 sm:mb-20 px-4">
            <button
              onClick={() => setShowLogin(true)}
              className="w-full sm:w-auto px-8 sm:px-12 py-5 sm:py-6 bg-gradient-to-tr from-cyan-500 to-blue-600 text-white rounded-[2rem] text-xs sm:text-sm font-black uppercase tracking-widest shadow-2xl shadow-cyan-500/40 hover:scale-105 sm:hover:scale-110 transition-all active:scale-95"
            >
              Launch Dashboard
            </button>
            <button
              onClick={() => setShowJoinUs(true)}
              className="w-full sm:w-auto px-8 sm:px-12 py-5 sm:py-6 rounded-[2rem] border border-[var(--border-color)] bg-white/50 backdrop-blur-md text-[9px] sm:text-[10px] font-black uppercase tracking-[0.2em] sm:tracking-[0.3em] hover:bg-white transition-all"
            >
              Request Documentation
            </button>
          </div>
        </motion.div>

        {/* Dashboard Preview */}
        <motion.div
          initial={{ opacity: 0, y: 100 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1 }}
          className="relative max-w-6xl mx-auto group"
        >
          <div className="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />
          <div className="rounded-[4rem] border border-white/20 bg-gradient-to-tr from-black/5 to-white/10 shadow-[0_80px_150px_-50px_rgba(0,186,212,0.3)] backdrop-blur-xl p-6 relative overflow-hidden">
            <div className="aspect-[16/9] bg-white rounded-[3.5rem] shadow-inner overflow-hidden relative border border-slate-100">
              <div className="absolute inset-x-0 top-0 h-12 bg-slate-50 border-b border-slate-100 flex items-center px-6 gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-yellow-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
              </div>
              <div className="flex h-full pt-12">
                {/* Sidebar Mockup */}
                <div className="w-1/4 h-full bg-slate-50/50 border-r border-slate-100 p-6 flex flex-col gap-4">
                  <div className="flex items-center gap-2 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
                    <div className="w-2 h-2 rounded-full bg-cyan-500" />
                    <div className="h-2 rounded-full bg-cyan-500/30 flex-1" />
                  </div>
                  {[1, 2, 3, 4].map(i => (
                    <div key={i} className="space-y-2 p-3 rounded-xl hover:bg-slate-100/50 transition-colors">
                      <div className="h-2 rounded-full bg-slate-200" style={{ width: `${Math.random() * 40 + 50}%` }} />
                      <div className="h-1.5 rounded-full bg-slate-100" style={{ width: '40%' }} />
                    </div>
                  ))}
                </div>

                {/* Chat Area Mockup */}
                <div className="flex-1 p-8 flex flex-col justify-between bg-gradient-to-br from-white to-slate-50/30">
                  {/* Messages */}
                  <div className="space-y-6">
                    {/* User Message */}
                    <div className="flex justify-end">
                      <div className="max-w-[70%] p-4 rounded-2xl rounded-tr-sm bg-indigo-500/10 border border-indigo-500/20">
                        <div className="h-2 rounded-full bg-indigo-300 w-32 mb-2" />
                        <div className="h-2 rounded-full bg-indigo-200 w-24" />
                      </div>
                    </div>

                    {/* AI Response */}
                    <div className="flex justify-start">
                      <div className="max-w-[80%] p-5 rounded-2xl rounded-tl-sm bg-white border border-slate-200 shadow-sm">
                        <div className="flex items-center gap-2 mb-3">
                          <Logo size={20} />
                          <div className="h-2 rounded-full bg-cyan-400 w-24" />
                        </div>
                        <div className="space-y-2">
                          <div className="h-2 rounded-full bg-slate-200 w-full" />
                          <div className="h-2 rounded-full bg-slate-200 w-5/6" />
                          <div className="h-2 rounded-full bg-slate-200 w-4/6" />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Input Box Mockup */}
                  <div className="flex items-center gap-3 p-4 rounded-3xl bg-white border border-slate-200 shadow-lg">
                    <Sparkles size={18} className="text-cyan-500" />
                    <div className="h-2 rounded-full bg-slate-100 flex-1" />
                    <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600" />
                  </div>
                </div>
              </div>
              <div className="absolute inset-0 flex items-center justify-center bg-black/10 opacity-0 group-hover:opacity-100 transition-all duration-500 backdrop-blur-sm">
                <motion.div
                  initial={{ scale: 0.9 }}
                  whileHover={{ scale: 1.05 }}
                  className="relative"
                >
                  {/* Animated Pulse Ring */}
                  <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 animate-ping opacity-20" />

                  {/* Main Card */}
                  <div className="relative px-8 py-5 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full shadow-2xl shadow-cyan-500/50 cursor-pointer group/btn border border-white/20">
                    <div className="flex items-center gap-3">
                      {/* Animated Icon */}
                      <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">
                        <Play size={14} className="text-white fill-white ml-0.5" />
                      </div>

                      {/* Text */}
                      <div className="flex flex-col items-start">
                        <span className="text-white text-xs font-black uppercase tracking-[0.2em] leading-none">Live Intelligence</span>
                        <span className="text-white/70 text-[8px] font-bold uppercase tracking-widest mt-1">Neural Dashboard Active</span>
                      </div>

                      {/* Pulse Indicator */}
                      <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse shadow-lg shadow-green-400/50" />
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Trusted By Banner */}
      <section className="py-12 sm:py-16 md:py-20 border-y border-[var(--border-color)] bg-white/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <p className="text-[9px] sm:text-[10px] font-black uppercase tracking-[0.3em] sm:tracking-[0.4em] text-[var(--text-muted)] text-center mb-8 sm:mb-12">Empowering Global Enterprises</p>
          <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-10 md:gap-16 lg:gap-32 grayscale opacity-30">
            {['GLOBAL CORP', 'TALENT-P', 'NEURAL-X', 'DATA-CORE', 'PULSE-TECH'].map((name, i) => (
              <span key={i} className="text-lg sm:text-xl md:text-2xl font-black italic tracking-tighter">{name}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Section - Expanded */}
      <section className="py-16 sm:py-24 md:py-32 lg:py-40 px-4 sm:px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-10 sm:gap-16 md:gap-20 items-center mb-20 sm:mb-32 md:mb-40">
            <motion.div initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
              <h3 className="text-3xl sm:text-4xl md:text-5xl font-black italic uppercase tracking-tighter mb-6 sm:mb-8 leading-tight">
                INDEX MILLIONS OF <br /><span className="text-cyan-500">DATA RECORDS</span> IN SECONDS
              </h3>
              <p className="text-[var(--text-muted)] text-sm sm:text-base leading-relaxed mb-8 sm:mb-10 font-medium">
                Our proprietary RAG (Retrieval Augmented Generation) engine slices through complex CSV, Excel, and PDF files. Use Gemini-3 to chat with your spreadsheets as if they were teammates.
              </p>
              <div className="grid grid-cols-2 gap-4 sm:gap-6">
                {[
                  { icon: <Binary className="text-blue-500" />, label: "Vector Search" },
                  { icon: <Workflow className="text-cyan-500" />, label: "ETL Pipelines" },
                  { icon: <Layers className="text-indigo-500" />, label: "Multi-Source" },
                  { icon: <MousePointer2 className="text-emerald-500" />, label: "One-Click Ingest" }
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-2 sm:gap-3 p-3 sm:p-5 rounded-2xl sm:rounded-3xl bg-white border border-slate-100 shadow-sm hover:border-cyan-500 transition-colors">
                    {item.icon}
                    <span className="text-[8px] sm:text-[10px] font-black uppercase tracking-widest">{item.label}</span>
                  </div>
                ))}
              </div>
            </motion.div>
            <div className="relative">
              <div className="aspect-square rounded-[3rem] sm:rounded-[4rem] bg-cyan-500/5 border border-cyan-500/10 flex items-center justify-center">
                <div className="relative w-32 h-32 sm:w-40 sm:h-40 md:w-48 md:h-48">
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 20, ease: "linear" }} className="absolute inset-0 border-2 border-dashed border-cyan-500/30 rounded-full" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Logo size={60} className="sm:w-20 sm:h-20" />
                  </div>
                </div>
              </div>
              {/* Floating elements */}
              <motion.div animate={{ y: [0, -20, 0] }} transition={{ repeat: Infinity, duration: 4 }} className="absolute -top-6 sm:-top-10 -right-6 sm:-right-10 p-4 sm:p-6 bg-white rounded-2xl sm:rounded-3xl shadow-2xl border border-slate-100">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-[8px] sm:text-[10px] font-black uppercase">Live Indexing</span>
                </div>
              </motion.div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 md:gap-10 text-center mb-20 sm:mb-32 md:mb-40">
            {[
              { title: "Infrastructure", href: "/infrastructure", icon: <Database />, desc: "Explore our zero-latency neural backbone architecture." },
              { title: "Evolutionary Vision", href: "/vision", icon: <Eye />, desc: "Our roadmap for autonomous business intelligence." },
              { title: "Fortress Security", href: "/security", icon: <Shield />, desc: "Zero-trust military grade data encryption protocols." }
            ].map((card, i) => (
              <Link href={card.href} key={i}>
                <motion.div whileHover={{ scale: 1.05 }} className="p-8 sm:p-10 md:p-12 rounded-[2.5rem] sm:rounded-[3rem] bg-[var(--card-bg)] border border-[var(--border-color)] hover:border-cyan-500 transition-all cursor-pointer group">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 rounded-2xl bg-black/5 text-cyan-500 flex items-center justify-center mx-auto mb-6 sm:mb-8 group-hover:bg-cyan-500 group-hover:text-white transition-all">
                    {card.title === "Infrastructure" ? <Layers /> : card.title === "Evolutionary Vision" ? <Sparkles /> : <Shield />}
                  </div>
                  <h4 className="text-lg sm:text-xl font-black italic uppercase mb-3 sm:mb-4">{card.title}</h4>
                  <p className="text-[var(--text-muted)] text-xs sm:text-sm leading-relaxed mb-4 sm:mb-6">{card.desc}</p>
                  <span className="text-[9px] sm:text-[10px] font-black uppercase tracking-[0.2em] sm:tracking-[0.3em] text-cyan-500">Exploration Protocol →</span>
                </motion.div>
              </Link>
            ))}
          </div>

          {/* New Section: Intelligence Workflow */}
          <div className="py-32 border-t border-[var(--border-color)]">
            <div className="text-center mb-20">
              <h3 className="text-4xl font-black italic uppercase mb-4">The TalentPulse Workflow</h3>
              <p className="text-[var(--text-muted)] uppercase text-[10px] font-black tracking-widest">Three steps to organizational clarity</p>
            </div>
            <div className="grid md:grid-cols-3 gap-8 relative">
              <div className="absolute top-1/2 left-0 w-full h-px bg-slate-100 -z-10 hidden md:block" />
              {[
                { step: "01", title: "Ingest", desc: "Upload any structured or unstructured business document." },
                { step: "02", title: "Process", desc: "Neural engines index data into multi-dimensional vectors." },
                { step: "03", title: "Query", desc: "Interact with your data through natural language conversations." }
              ].map((item, i) => (
                <div key={i} className="p-10 bg-white rounded-[3rem] border border-slate-100 shadow-xl text-center">
                  <span className="text-5xl font-black text-slate-100 mb-6 block">{item.step}</span>
                  <h4 className="text-xl font-black italic uppercase mb-4">{item.title}</h4>
                  <p className="text-[var(--text-muted)] text-sm">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-40 px-6 bg-slate-50">
        <div className="max-w-4xl mx-auto">
          <h3 className="text-4xl font-black italic uppercase mb-20 text-center">Frequently Asked Questions</h3>
          <div className="space-y-6">
            {[
              { q: "What is Gemini-3 integration?", a: "Gemini-3 provides our platform with state-of-the-art reasoning capabilities, allowing for deep data analysis beyond simple keyword matching." },
              { q: "How secure is my institutional data?", a: "We use SOC-2 compliant encryption and zero-trust architecture. Your data never leaves your specialized vector environment." },
              { q: "Can I upload multiple file types at once?", a: "Yes, our engine supports PDF, CSV, Excel, and Word documents in a unified batch ingestion process." },
              { q: "Does it support real-time chart generation?", a: "Absolutely. Our 'Visualization Intelligence' module can turn any retrieved numeric trend into a bar, line, or pie chart instantly." },
              { q: "Is training required for employees?", a: "No. TalentPulse is designed for natural conversation. If you can chat, you can analyze your business data." }
            ].map((faq, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="p-8 bg-white rounded-3xl border border-slate-200 hover:border-cyan-500 transition-all"
              >
                <h4 className="text-lg font-black uppercase italic mb-4 flex items-center gap-4">
                  <span className="text-cyan-500 text-2xl">?</span> {faq.q}
                </h4>
                <p className="text-[var(--text-muted)] text-sm font-medium leading-relaxed">{faq.a}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* New Section: Global Network Nodes */}
      <section className="py-60 px-6 bg-white overflow-hidden relative">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1500px] h-[1500px] bg-cyan-600/5 blur-[200px] rounded-full -z-10" />
        <div className="max-w-7xl mx-auto text-center">
          <h3 className="text-5xl md:text-8xl font-black italic uppercase mb-16 tracking-tighter">GLOBAL <span className="text-cyan-500">NODES</span></h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-12">
            {[
              { label: "Active Connections", value: "2.4M" },
              { label: "Data Indexed", value: "850TB" },
              { label: "Neural Speed", value: "0.1ms" },
              { label: "System Uptime", value: "99.9%" }
            ].map((stat, i) => (
              <div key={i} className="flex flex-col gap-2">
                <span className="text-5xl font-black italic text-slate-900 leading-none">{stat.value}</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-cyan-600">{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-40 px-6 bg-black text-white text-center relative overflow-hidden">
        <div className="absolute inset-0 opacity-20 pointer-events-none">
          <div className="absolute top-[50%] left-[50%] -translate-x-1/2 -translate-y-1/2 w-[1200px] h-[1200px] bg-cyan-500 blur-[200px] rounded-full" />
        </div>
        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="relative z-10 max-w-4xl mx-auto">
          <h2 className="text-5xl md:text-8xl font-black tracking-tighter italic uppercase mb-12 leading-none">
            READY TO <span className="text-cyan-400">PULSE</span>?
          </h2>
          <p className="text-gray-400 text-lg mb-16 max-w-2xl mx-auto leading-relaxed">
            Join the elite tier of data-driven enterprises. Harness the power of TalentPulse and transform your institutional intelligence today.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-6 mt-8">
            <button
              onClick={() => setShowLogin(true)}
              className="px-12 py-6 bg-white text-black rounded-[2.5rem] font-black uppercase text-xs tracking-[0.3em] hover:scale-105 active:scale-95 transition-all shadow-[0_20px_60px_rgba(255,255,255,0.2)]"
            >
              Initialize Command
            </button>
            <button
              onClick={() => setShowJoinUs(true)}
              className="px-12 py-6 bg-transparent border-2 border-cyan-500 text-cyan-400 rounded-[2.5rem] font-black uppercase text-xs tracking-[0.3em] hover:bg-cyan-500 hover:text-white hover:scale-105 active:scale-95 transition-all shadow-[0_0_40px_rgba(6,182,212,0.2)]"
            >
              Join Waiting List
            </button>
          </div>
        </motion.div>
      </section>


      {/* Modern Footer */}
      <footer className="py-20 px-6 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-center gap-12 border-b border-[var(--border-color)] pb-20 mb-10">
          <div className="flex flex-col items-center md:items-start gap-4">
            <div className="flex items-center gap-3">
              <Logo size={40} />
              <span className="text-2xl font-black italic uppercase tracking-tighter">TALENTPULSE</span>
            </div>
            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-[var(--text-muted)]">Unified Intelligence Agency</p>
          </div>
          <div className="flex gap-16 text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">
            <div className="flex flex-col gap-5">
              <span className="text-cyan-500">Connect</span>
              <a href="#" className="hover:text-black">LinkedIn</a>
              <a href="#" className="hover:text-black">Terminal</a>
            </div>
            <div className="flex flex-col gap-5">
              <span className="text-cyan-500">Legal</span>
              <a href="#" className="hover:text-black">Privacy</a>
              <a href="#" className="hover:text-black">Terms</a>
            </div>
          </div>
        </div>
        <p className="text-[9px] font-bold text-center uppercase tracking-[0.5em] text-[var(--text-muted)] opacity-50 italic">
          v2.5.0-Preview // Military Encryption Level AES-256 Enabled
        </p>
      </footer>

      {/* Login Modal */}
      <AnimatePresence>
        {showLogin && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[200] bg-black/80 backdrop-blur-2xl flex items-center justify-center p-4"
            onClick={() => setShowLogin(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 30 }} animate={{ scale: 1, y: 0 }}
              className="w-full max-w-md bg-white rounded-[3.5rem] p-12 shadow-2xl relative overflow-hidden"
              onClick={e => e.stopPropagation()}
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-600" />

              <div className="flex flex-col items-center mb-12 text-center">
                <div className="w-20 h-20 rounded-3xl bg-slate-50 border border-slate-100 shadow-xl flex items-center justify-center mb-6">
                  <Logo size={60} />
                </div>
                <h3 className="text-3xl font-black italic uppercase tracking-tighter">System Login</h3>
                <p className="text-[10px] font-black uppercase tracking-[0.4em] text-cyan-600/60 mt-2 italic">Intelligence Protocol</p>
              </div>

              <form onSubmit={handleLogin} className="space-y-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] ml-4 italic">Identifier</label>
                  <div className="relative group">
                    <User size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-[var(--text-muted)] group-focus-within:text-cyan-500 transition-colors" />
                    <input
                      type="email" required value={email} onChange={e => setEmail(e.target.value)}
                      placeholder="developer.mspl@gmail.com"
                      className="w-full py-5 pl-16 pr-8 bg-slate-50 border border-transparent focus:border-cyan-500 rounded-3xl text-sm font-bold transition-all outline-none"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] ml-4 italic">Access Code</label>
                  <div className="relative group">
                    <Settings size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-[var(--text-muted)] group-focus-within:text-cyan-500 transition-colors" />
                    <input
                      type="password" required value={password} onChange={e => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full py-5 pl-16 pr-8 bg-slate-50 border border-transparent focus:border-cyan-500 rounded-3xl text-sm font-bold transition-all outline-none"
                    />
                  </div>
                </div>

                {error && <p className="text-red-500 text-[10px] font-black text-center uppercase tracking-widest italic animate-bounce">{error}</p>}

                <button
                  type="submit" disabled={loading}
                  className="w-full py-6 rounded-3xl bg-black text-white font-black uppercase text-[11px] tracking-widest hover:scale-[1.02] active:scale-95 transition-all shadow-2xl shadow-black/20 flex items-center justify-center gap-3 disabled:opacity-50"
                >
                  {loading ? <Loader2 className="animate-spin" size={16} /> : <Zap size={16} />}
                  {loading ? 'Authorizing...' : 'Initialize Session'}
                </button>
              </form>

              <button
                onClick={() => setShowLogin(false)}
                className="w-full mt-6 py-4 text-[10px] font-black uppercase text-[var(--text-muted)] hover:text-red-500 transition-colors italic tracking-widest"
              >
                Abort Connection
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Join Us Modal */}
      <AnimatePresence>
        {showJoinUs && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[200] bg-black/80 backdrop-blur-2xl flex items-start sm:items-center justify-center p-4 overflow-y-auto"
            onClick={() => setShowJoinUs(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 30 }} animate={{ scale: 1, y: 0 }}
              className="w-full max-w-2xl bg-white rounded-[2rem] sm:rounded-[3.5rem] p-6 sm:p-12 shadow-2xl relative my-auto max-h-[95vh] sm:max-h-none overflow-y-auto sm:overflow-visible"
              onClick={e => e.stopPropagation()}
            >
              <div className="flex flex-col items-center mb-12 text-center">
                <div className="w-20 h-20 rounded-3xl bg-slate-50 border border-slate-100 shadow-xl flex items-center justify-center mb-6">
                  <Logo size={60} />
                </div>
                <h3 className="text-3xl font-black italic uppercase tracking-tighter">Join the Waitlist</h3>
                <p className="text-[10px] font-black uppercase tracking-[0.4em] text-cyan-600/60 mt-2 italic">Priority Access Request</p>
              </div>

              {leadSuccess ? (
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 p-6 rounded-2xl text-center">
                  <h4 className="font-black uppercase tracking-widest mb-2">Success</h4>
                  <p className="font-medium text-sm">{leadSuccess}</p>
                </div>
              ) : (
                <form onSubmit={handleLeadSubmit} className="space-y-5">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div className="space-y-1">
                      <label className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] ml-4 italic">Full Name *</label>
                      <input type="text" required value={leadForm.name} onChange={e => setLeadForm({...leadForm, name: e.target.value})} className="w-full py-4 px-6 bg-slate-50 border border-transparent focus:border-cyan-500 rounded-2xl text-sm font-bold transition-all outline-none text-slate-900" placeholder="John Doe" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] ml-4 italic">Email Address *</label>
                      <input type="email" required value={leadForm.email} onChange={e => setLeadForm({...leadForm, email: e.target.value})} className="w-full py-4 px-6 bg-slate-50 border border-transparent focus:border-cyan-500 rounded-2xl text-sm font-bold transition-all outline-none text-slate-900" placeholder="john@company.com" />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div className="space-y-1">
                      <label className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] ml-4 italic">Phone Number *</label>
                      <input type="tel" required value={leadForm.phone} onChange={e => setLeadForm({...leadForm, phone: e.target.value})} className="w-full py-4 px-6 bg-slate-50 border border-transparent focus:border-cyan-500 rounded-2xl text-sm font-bold transition-all outline-none text-slate-900" placeholder="+1 (555) 000-0000" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] ml-4 italic">Company Name *</label>
                      <input type="text" required value={leadForm.company} onChange={e => setLeadForm({...leadForm, company: e.target.value})} className="w-full py-4 px-6 bg-slate-50 border border-transparent focus:border-cyan-500 rounded-2xl text-sm font-bold transition-all outline-none text-slate-900" placeholder="Acme Corp" />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] ml-4 italic">Service Interested In *</label>
                    <select required value={leadForm.service} onChange={e => setLeadForm({...leadForm, service: e.target.value})} className="w-full py-4 px-6 bg-slate-50 border border-transparent focus:border-cyan-500 rounded-2xl text-sm font-bold transition-all outline-none text-slate-900 appearance-none cursor-pointer">
                      <option value="" disabled>Select a service</option>
                      <option value="Enterprise AI Orchestration">Enterprise AI Orchestration</option>
                      <option value="Data Infrastructure">Data Infrastructure</option>
                      <option value="Custom Model Training">Custom Model Training</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div className="space-y-2 pt-2">
                    <div className="flex justify-between items-center px-4">
                      <label className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] italic">Estimated Budget (Optional)</label>
                      <div className="flex items-center gap-1 bg-cyan-50 px-3 py-1 rounded-lg border border-cyan-100">
                        <span className="text-[10px] font-black text-cyan-600">₹</span>
                        <input 
                          type="text" 
                          value={leadForm.budget} 
                          onChange={e => {
                            const val = e.target.value.replace(/\D/g, '');
                            if (parseInt(val) > 10000000) return; // Cap at 1Cr
                            setLeadForm({...leadForm, budget: val || '0'});
                          }}
                          className="w-20 text-[10px] font-black text-cyan-600 bg-transparent outline-none border-none p-0"
                        />
                      </div>
                    </div>
                    <input 
                      type="range" min="0" max="10000000" step="50000" 
                      value={leadForm.budget} onChange={e => setLeadForm({...leadForm, budget: e.target.value})} 
                      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                    />
                    <div className="flex justify-between px-2 text-[10px] font-bold text-slate-400">
                      <span>₹0</span>
                      <span>₹1 Cr+</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] ml-4 italic">Message (Optional)</label>
                    <textarea value={leadForm.message} onChange={e => setLeadForm({...leadForm, message: e.target.value})} rows={3} className="w-full py-4 px-6 bg-slate-50 border border-transparent focus:border-cyan-500 rounded-2xl text-sm font-medium transition-all outline-none text-slate-900 resize-none" placeholder="Tell us about your project..." />
                  </div>

                  {leadError && <p className="text-red-500 text-[10px] font-black text-center uppercase tracking-widest italic">{leadError}</p>}

                  <button type="submit" disabled={leadLoading} className="w-full py-5 rounded-2xl bg-black text-white font-black uppercase text-[11px] tracking-widest hover:scale-[1.02] active:scale-95 transition-all shadow-xl flex items-center justify-center gap-2 disabled:opacity-50 mt-4">
                    {leadLoading ? <Loader2 className="animate-spin" size={16} /> : <Zap size={16} />}
                    {leadLoading ? 'Submitting...' : 'Submit Request'}
                  </button>
                </form>
              )}

              <button onClick={() => setShowJoinUs(false)} className="w-full mt-4 py-3 text-[10px] font-black uppercase text-[var(--text-muted)] hover:text-slate-900 transition-colors italic tracking-widest">
                Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
