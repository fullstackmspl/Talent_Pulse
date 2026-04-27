'use client';

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, User, Bot, Sparkles, Menu, Plus, MessageSquare, Settings, FileText, Copy, Check, X, ArrowDown, Download, Volume2, Trash2, Command, Keyboard, Upload, FileUp, Database, Loader2, Globe, FileDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ChartRenderer from '../ChartRenderer';
import Logo from '../Logo';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { jsPDF } from 'jspdf';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'https://talentpulse.meander.one/api';

interface ChatSession {
    id: string;
    title: string;
    messages: { role: 'user' | 'ai'; content: string; options?: string[] }[];
    timestamp: number;
}

export default function Dashboard() {
    const router = useRouter();
    const [messages, setMessages] = useState<{ role: 'user' | 'ai'; content: string; options?: string[] }[]>([]);
    const [history, setHistory] = useState<ChatSession[]>([]);
    const [currentChatId, setCurrentChatId] = useState<string | null>(null);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
    const [showScrollBtn, setShowScrollBtn] = useState(false);
    const [latency, setLatency] = useState<number | null>(null);
    const [showShortcuts, setShowShortcuts] = useState(false);
    const [theme, setTheme] = useState<'light' | 'dark'>('dark');
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [showKB, setShowKB] = useState(false);
    const [files, setFiles] = useState<{ name: string, uploaded_at: string }[]>([]);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [fileToDelete, setFileToDelete] = useState<string | null>(null);
    const [showChatDeleteConfirm, setShowChatDeleteConfirm] = useState(false);
    const [chatToDelete, setChatToDelete] = useState<string | null>(null);
    const [showSettings, setShowSettings] = useState(false);
    const [groqKey, setGroqKey] = useState('');
    const [geminiKey, setGeminiKey] = useState('');

    // New State for Features
    const [linkInput, setLinkInput] = useState('');
    const [kbTab, setKbTab] = useState<'file' | 'link'>('file');

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    // Initial setup
    useEffect(() => {
        const isAuth = localStorage.getItem('genius_auth') === 'true';
        const hasToken = !!localStorage.getItem('talent_pulse_token');
        if (!isAuth || !hasToken) {
            localStorage.removeItem('genius_auth');
            router.push('/');
            return;
        }
        setIsLoggedIn(true);

        const savedHistory = localStorage.getItem('genius_history');
        if (savedHistory) setHistory(JSON.parse(savedHistory));

        const savedTheme = localStorage.getItem('talentpulse_theme') as 'light' | 'dark';
        if (savedTheme) {
            setTheme(savedTheme);
            document.documentElement.setAttribute('data-theme', savedTheme);
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
        }

        const token = localStorage.getItem('talent_pulse_token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        // Fetch Uploaded Files
        axios.get(`${API_BASE}/files`, { headers })
            .then(res => setFiles(res.data.data || []))
            .catch(e => console.error("Failed to load files", e));
    }, [router]);

    const handleLogout = () => {
        localStorage.removeItem('genius_auth');
        setIsLoggedIn(false);
        router.push('/');
    };

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('talentpulse_theme', newTheme);
    };

    const handleUpdateKeys = async () => {
        if (!groqKey && !geminiKey) {
            toast.error("Please enter at least one API key.");
            return;
        }

        const toastId = toast.loading("Updating secure protocols...");
        const token = localStorage.getItem('talent_pulse_token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        try {
            const res = await axios.post(`${API_BASE}/config/api-keys`, {
                groq_api_key: groqKey,
                gemini_api_key: geminiKey
            }, { headers });

            if (res.data.status === 'success') {
                toast.success("AI Protocols Updated Successfully", { id: toastId });
                setGroqKey('');
                setGeminiKey('');
                setShowSettings(false);
            } else {
                toast.error(res.data.message, { id: toastId });
            }
        } catch (e: any) {
            toast.error("Protocol update failed. Verify authentication.", { id: toastId });
        }
    };

    useEffect(() => {
        if (history.length > 0) {
            localStorage.setItem('genius_history', JSON.stringify(history));
        }
    }, [history]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                startNewChat();
            }
            if (e.key === 'Escape') {
                setShowShortcuts(false);
                setShowKB(false);
                setShowDeleteConfirm(false);
                setShowChatDeleteConfirm(false);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    const initiateDelete = (fileName: string) => {
        setFileToDelete(fileName);
        setShowDeleteConfirm(true);
    };

    const confirmDelete = async () => {
        if (!fileToDelete) return;

        const deletingToast = toast.loading(`Deleting ${fileToDelete}...`);
        const token = localStorage.getItem('talent_pulse_token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        try {
            const res = await axios.delete(`${API_BASE}/files/${encodeURIComponent(fileToDelete)}`, { headers });

            if (res.data.status === 'success') {
                toast.success(`Deleted ${fileToDelete} successfully!`, { id: deletingToast });
                setFiles(prev => prev.filter(f => f.name !== fileToDelete));
            } else {
                toast.error(`Failed to delete ${fileToDelete}`, { id: deletingToast });
            }
        } catch (error: any) {
            const errMsg = error.response?.data?.detail || error.message || 'Network error';
            toast.error(`Error: ${errMsg}`, { id: deletingToast });
        } finally {
            setShowDeleteConfirm(false);
            setFileToDelete(null);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
        const target = e.currentTarget;
        const isAtBottom = target.scrollHeight - target.scrollTop <= target.clientHeight + 100;
        setShowScrollBtn(!isAtBottom);
    };

    const startNewChat = () => {
        setMessages([]);
        setCurrentChatId(null);
        if (window.innerWidth < 1024) setSidebarOpen(false);
    };

    const loadChat = (chat: ChatSession) => {
        setMessages(chat.messages);
        setCurrentChatId(chat.id);
        if (window.innerWidth < 1024) setSidebarOpen(false);
    };

    const initiateDeleteChat = (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        setChatToDelete(id);
        setShowChatDeleteConfirm(true);
    };

    const confirmDeleteChat = () => {
        if (!chatToDelete) return;

        const newHistory = history.filter(h => h.id !== chatToDelete);
        setHistory(newHistory);
        localStorage.setItem('genius_history', JSON.stringify(newHistory));
        if (currentChatId === chatToDelete) startNewChat();

        setShowChatDeleteConfirm(false);
        setChatToDelete(null);
        toast.success('Chat deleted successfully');
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        const processingToast = toast.loading(`Processing ${file.name}...`);
        const formData = new FormData();
        formData.append('file', file);
        
        const token = localStorage.getItem('talent_pulse_token');
        const headers = token ? { Authorization: `Bearer ${token}` } : { 'Content-Type': 'multipart/form-data' };
        if (token) (headers as any)['Content-Type'] = 'multipart/form-data';

        try {
            const res = await axios.post(`${API_BASE}/upload`, formData, { headers });

            if (res.data.status === 'success') {
                toast.success(`Indexed ${file.name} successfully!`, { id: processingToast });
                setFiles(prev => [...prev, { name: file.name, uploaded_at: new Date().toISOString() }]);
                setShowKB(false);
            } else {
                toast.error(`Failed to process ${file.name}`, { id: processingToast });
            }
        } catch (error: any) {
            const errMsg = error.response?.data?.detail || error.message || 'Network error';
            toast.error(`Error: ${errMsg}`, { id: processingToast });
        } finally {
            setUploading(false);
        }
    };

    const handleLinkSubmit = async () => {
        if (!linkInput) return;
        setUploading(true);
        const toastId = toast.loading("Scanning neural web...");
        const token = localStorage.getItem('talent_pulse_token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        try {
            const res = await axios.post(`${API_BASE}/process-link`, { url: linkInput }, { headers });
            if (res.data.status === 'success') {
                toast.success("Web Link Indexed Successfully", { id: toastId });
                setFiles(prev => [...prev, { name: linkInput, uploaded_at: new Date().toISOString() }]);
                setLinkInput('');
                setShowKB(false);
            } else {
                toast.error(res.data.message, { id: toastId });
            }
        } catch (e: any) {
            toast.error("Link analysis failed. Verify URL.", { id: toastId });
        } finally {
            setUploading(false);
        }
    };

    const exportToPDF = () => {
        if (messages.length === 0) {
            toast.error("No intelligence to export.");
            return;
        }

        const doc = new jsPDF();
        doc.setFontSize(20);
        doc.setTextColor(6, 182, 212);
        doc.text("TALENTPULSE INTELLIGENCE REPORT", 20, 20);

        doc.setFontSize(10);
        doc.setTextColor(100);
        doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 30);

        let y = 45;

        messages.forEach((msg, i) => {
            if (y > 270) {
                doc.addPage();
                y = 20;
            }

            doc.setFontSize(10);
            doc.setFont("helvetica", "bold");
            const roleColor = msg.role === 'user' ? [59, 130, 246] : [6, 182, 212];
            doc.setTextColor(roleColor[0], roleColor[1], roleColor[2]);
            const role = msg.role === 'user' ? ' QUERY' : ' INTELLIGENCE';
            doc.text(role, 20, y);
            y += 5;

            doc.setFont("helvetica", "normal");
            doc.setTextColor(0, 0, 0);

            // Basic cleaning for PDF text
            // Remove markdown symbols for cleaner PDF
            const cleanContent = msg.content.replace(/[*#`]/g, '');
            const splitText = doc.splitTextToSize(cleanContent, 170);

            doc.text(splitText, 20, y);
            y += (splitText.length * 5) + 10;
        });

        doc.save(`TalentPulse_Analysis_${Date.now()}.pdf`);
        toast.success("Intelligence Report Exported");
    };

    const sendMessage = async (text: string = input) => {
        if (!text.trim()) return;

        if (text === 'Upload New Resume') {
            setShowKB(true);
            setInput('');
            return; // Don't send this to backend, just open the UI
        }

        const newMessages = [...messages, { role: 'user' as const, content: text }];
        setMessages(newMessages);
        setInput('');
        setLoading(true);
        const startTime = Date.now();
        
        const token = localStorage.getItem('talent_pulse_token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        try {
            const res = await axios.post(`${API_BASE}/chat`, { query: text }, { headers });
            const aiResponse = res.data.data?.response || res.data.response || res.data.message;
            const options = res.data.data?.options || res.data.options;
            const finalMessages = [...newMessages, { role: 'ai' as const, content: aiResponse, options }];

            setLatency(Date.now() - startTime);
            setMessages(finalMessages);

            if (!currentChatId) {
                const newId = Date.now().toString();
                const newSession: ChatSession = {
                    id: newId,
                    title: text.slice(0, 30) + (text.length > 30 ? '...' : ''),
                    messages: finalMessages,
                    timestamp: Date.now()
                };
                const updatedHistory = [newSession, ...history];
                setHistory(updatedHistory);
                localStorage.setItem('genius_history', JSON.stringify(updatedHistory));
                setCurrentChatId(newId);
            } else {
                const updatedHistory = history.map(h =>
                    h.id === currentChatId ? { ...h, messages: finalMessages } : h
                );
                setHistory(updatedHistory);
                localStorage.setItem('genius_history', JSON.stringify(updatedHistory));
            }

        } catch (error: any) {
            setMessages(prev => [...prev, { role: 'ai', content: `⚠️ **Network Error**: Unable to reach TalentPulse server. Please ensure the backend is running and try again.` }]);
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text: string, index: number) => {
        navigator.clipboard.writeText(text);
        setCopiedIndex(index);
        setTimeout(() => setCopiedIndex(null), 2000);
    };

    const downloadReport = (content: string) => {
        const element = document.createElement("a");
        const file = new Blob([content], { type: 'text/markdown' });
        element.href = URL.createObjectURL(file);
        element.download = `TalentPulse_Analysis.md`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    const speak = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text.replace(/[#*`]/g, ''));
        utterance.rate = 1.0;
        speechSynthesis.speak(utterance);
    };

    if (!isLoggedIn) return null;

    return (
        <main className="flex h-screen bg-[var(--background)] text-[var(--foreground)] overflow-hidden transition-colors duration-300">
            {/* Overlays */}
            <AnimatePresence>
                {sidebarOpen && window.innerWidth < 1024 && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setSidebarOpen(false)} className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 lg:hidden" />
                )}

                {showKB && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/80 backdrop-blur-md z-[100] flex items-center justify-center p-4">
                        <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-[2.5rem] p-10 max-w-md w-full shadow-2xl relative overflow-hidden" onClick={e => e.stopPropagation()}>
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-600" />
                            <div className="flex items-center gap-4 mb-6">
                                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 flex items-center justify-center text-cyan-500">
                                    <Database size={24} />
                                </div>
                                <div>
                                    <h2 className="text-xl font-black uppercase italic tracking-tight">KNOWLEDGE BANK</h2>
                                    <p className="text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-widest">Feed the TalentPulse Engine</p>
                                </div>
                            </div>

                            <div className="flex p-1 bg-[var(--sidebar-bg)] rounded-xl mb-6 border border-[var(--border-color)]">
                                <button onClick={() => setKbTab('file')} className={`flex-1 py-2 text-[10px] font-bold uppercase tracking-widest rounded-lg transition-all ${kbTab === 'file' ? 'bg-cyan-500 text-white shadow-lg' : 'text-[var(--text-muted)] hover:text-[var(--foreground)]'}`}>File Upload</button>
                                <button onClick={() => setKbTab('link')} className={`flex-1 py-2 text-[10px] font-bold uppercase tracking-widest rounded-lg transition-all ${kbTab === 'link' ? 'bg-cyan-500 text-white shadow-lg' : 'text-[var(--text-muted)] hover:text-[var(--foreground)]'}`}>Web Link</button>
                            </div>

                            <div className="space-y-6">
                                {kbTab === 'file' ? (
                                    <label className="block w-full">
                                        <div className="w-full h-44 border-2 border-dashed border-[var(--border-color)] rounded-3xl flex flex-col items-center justify-center gap-3 hover:border-cyan-500 hover:bg-cyan-500/5 cursor-pointer transition-all group relative">
                                            {uploading ? (
                                                <div className="flex flex-col items-center gap-3">
                                                    <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
                                                    <span className="text-[10px] font-black uppercase text-cyan-500 animate-pulse">Processing Document...</span>
                                                </div>
                                            ) : (
                                                <>
                                                    <Upload size={40} className="text-[var(--text-muted)] opacity-30 group-hover:text-cyan-500 group-hover:opacity-100 transition-all" />
                                                    <span className="text-[10px] font-black uppercase text-[var(--text-muted)] group-hover:text-[var(--foreground)]">Drop PDF/CSV/Excel here</span>
                                                    <input type="file" className="hidden" accept=".pdf,.csv,.xlsx,.xls" onChange={handleFileUpload} />
                                                </>
                                            )}
                                        </div>
                                    </label>
                                ) : (
                                    <div className="space-y-4">
                                        <div className="relative group">
                                            <Globe className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)] group-focus-within:text-cyan-500 transition-colors" size={18} />
                                            <input
                                                type="text"
                                                placeholder="https://example.com/data"
                                                value={linkInput}
                                                onChange={(e) => setLinkInput(e.target.value)}
                                                className="w-full bg-[var(--sidebar-bg)] border border-[var(--border-color)] rounded-xl py-4 pl-12 pr-4 text-xs font-bold focus:outline-none focus:border-cyan-500 transition-all"
                                            />
                                        </div>
                                        <button
                                            onClick={handleLinkSubmit}
                                            disabled={uploading || !linkInput}
                                            className="w-full py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-black uppercase text-[10px] tracking-widest shadow-lg hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                                        >
                                            {uploading ? 'Scanning...' : 'Analyze URL'}
                                        </button>
                                    </div>
                                )}
                            </div>
                            <button onClick={() => setShowKB(false)} className="w-full mt-6 py-4 rounded-2xl bg-[var(--sidebar-bg)] hover:bg-[var(--border-color)] text-[10px] font-black uppercase text-[var(--text-muted)] transition-all">Cancel protocol</button>
                        </motion.div>
                    </motion.div>
                )}

                {showDeleteConfirm && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/80 backdrop-blur-md z-[100] flex items-center justify-center p-4"
                        onClick={() => setShowDeleteConfirm(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-[2.5rem] p-10 max-w-md w-full shadow-2xl relative overflow-hidden"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 to-orange-600" />

                            <div className="flex items-center gap-4 mb-6">
                                <div className="w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center text-red-500">
                                    <Trash2 size={24} />
                                </div>
                                <div>
                                    <h2 className="text-xl font-black uppercase italic tracking-tight">CONFIRM DELETE</h2>
                                    <p className="text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-widest">This action cannot be undone</p>
                                </div>
                            </div>

                            <div className="mb-8 p-4 bg-[var(--sidebar-bg)] rounded-2xl border border-[var(--border-color)]">
                                <p className="text-sm text-[var(--text-muted)] mb-2 font-bold uppercase text-[10px] tracking-widest">File to delete:</p>
                                <p className="text-[var(--foreground)] font-bold truncate">{fileToDelete}</p>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShowDeleteConfirm(false)}
                                    className="flex-1 py-4 rounded-2xl bg-[var(--sidebar-bg)] hover:bg-[var(--border-color)] text-[10px] font-black uppercase text-[var(--text-muted)] transition-all border border-[var(--border-color)]"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={confirmDelete}
                                    className="flex-1 py-4 rounded-2xl bg-gradient-to-r from-red-500 to-orange-600 text-white font-black uppercase text-[10px] tracking-widest shadow-lg hover:scale-[1.02] active:scale-95 transition-all"
                                >
                                    Delete
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}

                {showChatDeleteConfirm && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/80 backdrop-blur-md z-[100] flex items-center justify-center p-4"
                        onClick={() => setShowChatDeleteConfirm(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-[2.5rem] p-10 max-w-md w-full shadow-2xl relative overflow-hidden"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 to-orange-600" />

                            <div className="flex items-center gap-4 mb-6">
                                <div className="w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center text-red-500">
                                    <MessageSquare size={24} />
                                </div>
                                <div>
                                    <h2 className="text-xl font-black uppercase italic tracking-tight">DELETE CHAT</h2>
                                    <p className="text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-widest">This action cannot be undone</p>
                                </div>
                            </div>

                            <div className="mb-8 p-4 bg-[var(--sidebar-bg)] rounded-2xl border border-[var(--border-color)]">
                                <p className="text-sm text-[var(--text-muted)] mb-2 font-bold uppercase text-[10px] tracking-widest">Chat to delete:</p>
                                <p className="text-[var(--foreground)] font-bold truncate">
                                    {chatToDelete ? history.find(h => h.id === chatToDelete)?.title || 'Chat' : ''}
                                </p>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShowChatDeleteConfirm(false)}
                                    className="flex-1 py-4 rounded-2xl bg-[var(--sidebar-bg)] hover:bg-[var(--border-color)] text-[10px] font-black uppercase text-[var(--text-muted)] transition-all border border-[var(--border-color)]"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={confirmDeleteChat}
                                    className="flex-1 py-4 rounded-2xl bg-gradient-to-r from-red-500 to-orange-600 text-white font-black uppercase text-[10px] tracking-widest shadow-lg hover:scale-[1.02] active:scale-95 transition-all"
                                >
                                    Delete
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}

                {showSettings && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/80 backdrop-blur-md z-[100] flex items-center justify-center p-4"
                        onClick={() => setShowSettings(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-[2.5rem] p-10 max-w-lg w-full shadow-2xl relative overflow-hidden"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-600" />

                            <div className="flex items-center gap-4 mb-8">
                                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 flex items-center justify-center text-cyan-500">
                                    <Settings size={24} />
                                </div>
                                <div>
                                    <h2 className="text-xl font-black uppercase italic tracking-tight">AI PROTOCOLS</h2>
                                    <p className="text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-widest">Configure API Engine Access</p>
                                </div>
                            </div>

                            <div className="space-y-6 mb-10">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-cyan-500 uppercase tracking-widest ml-1">Groq API Key (URL Brain)</label>
                                    <input 
                                        type="password"
                                        value={groqKey}
                                        onChange={(e) => setGroqKey(e.target.value)}
                                        placeholder="gsk_..."
                                        className="w-full bg-[var(--sidebar-bg)] border border-[var(--border-color)] rounded-2xl p-4 text-xs font-bold focus:outline-none focus:border-cyan-500 transition-all"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-blue-500 uppercase tracking-widest ml-1">Gemini API Key (File Brain)</label>
                                    <input 
                                        type="password"
                                        value={geminiKey}
                                        onChange={(e) => setGeminiKey(e.target.value)}
                                        placeholder="AIza..."
                                        className="w-full bg-[var(--sidebar-bg)] border border-[var(--border-color)] rounded-2xl p-4 text-xs font-bold focus:outline-none focus:border-blue-500 transition-all"
                                    />
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShowSettings(false)}
                                    className="flex-1 py-4 rounded-2xl bg-[var(--sidebar-bg)] hover:bg-[var(--border-color)] text-[10px] font-black uppercase text-[var(--text-muted)] transition-all border border-[var(--border-color)]"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleUpdateKeys}
                                    className="flex-1 py-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-black uppercase text-[10px] tracking-widest shadow-lg hover:scale-[1.02] active:scale-95 transition-all"
                                >
                                    Update Protocols
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Sidebar */}
            <motion.aside
                initial={false}
                animate={{ x: sidebarOpen ? 0 : -280, width: sidebarOpen ? 280 : 0, opacity: sidebarOpen ? 1 : 0 }}
                className={`fixed lg:relative z-40 h-full flex flex-col border-r border-[var(--border-color)] bg-[var(--sidebar-bg)] backdrop-blur-2xl transition-all duration-300 ease-in-out ${!sidebarOpen && 'lg:w-0'}`}
            >
                <div className="p-6 flex items-center justify-between border-b border-[var(--border-color)]">
                    <div className="flex items-center gap-3">
                        <Logo size={32} className="scale-125" />
                        <div className="flex flex-col">
                            <span className="font-black text-xs tracking-tight text-[var(--foreground)] italic uppercase leading-none">TALENTPULSE</span>
                            <span className="text-[9px] font-bold text-cyan-500/60 uppercase tracking-widest mt-1">AI Protocol</span>
                        </div>
                    </div>
                    <button onClick={() => setSidebarOpen(false)} className="lg:hidden p-1.5 hover:bg-[var(--border-color)] rounded-lg text-[var(--text-muted)]">
                        <X size={18} />
                    </button>
                </div>

                <div className="p-4 space-y-3">
                    <button onClick={() => setShowKB(true)} className="w-full flex items-center gap-3 p-4 rounded-2xl border border-[var(--border-color)] hover:border-cyan-500 hover:bg-cyan-500/5 transition-all group">
                        <Database size={18} className="text-cyan-500 group-hover:scale-110 transition-transform" />
                        <div className="text-left">
                            <p className="text-[10px] font-black uppercase text-cyan-500">KNOWLEDGE BANK</p>
                            <p className="text-[8px] font-bold text-[var(--text-muted)] opacity-60">Upload Data Files</p>
                        </div>
                    </button>

                    <button onClick={startNewChat} className="w-full flex items-center justify-center gap-3 p-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg hover:scale-[1.02] active:scale-95 transition-all text-[10px] font-black uppercase tracking-widest">
                        <Plus size={16} /> New Session
                    </button>
                    {!sidebarOpen && <div className="h-4" />}
                    <button onClick={exportToPDF} className="w-full flex items-center justify-center gap-3 p-3 rounded-2xl border border-[var(--border-color)] hover:border-cyan-500 hover:bg-cyan-500/5 transition-all text-[10px] font-black uppercase tracking-widest text-[var(--foreground)]">
                        <FileDown size={16} /> Export PDF Report
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto px-4 py-2 custom-scrollbar space-y-6">
                    <div>
                        <p className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-widest mb-4 italic px-2">Knowledge Assets</p>
                        <div className="space-y-1">
                            {files.length === 0 ? (
                                <p className="px-3 text-[10px] text-[var(--text-muted)] opacity-50 italic">No documents indexed yet.</p>
                            ) : (
                                files.map((f, i) => (
                                    <div key={i} className="flex items-center gap-3 p-3 text-xs rounded-xl border border-[var(--border-color)] bg-[var(--card-bg)] shadow-sm group">
                                        <FileText size={14} className="text-cyan-500" />
                                        <div className="flex-1 min-w-0">
                                            <p className="truncate font-bold text-[var(--foreground)]">{f.name}</p>
                                            <p className="text-[8px] text-[var(--text-muted)] truncate">{new Date(f.uploaded_at).toLocaleDateString()}</p>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                initiateDelete(f.name);
                                            }}
                                            className="opacity-0 group-hover:opacity-100 p-1.5 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
                                            title="Delete file"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    <div>
                        <p className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-widest mb-4 italic px-2">History</p>
                        <div className="space-y-1">
                            {history.map((chat) => (
                                <div key={chat.id} onClick={() => loadChat(chat)} className={`flex items-center gap-3 p-3 text-xs rounded-xl cursor-pointer transition-all group border ${currentChatId === chat.id ? 'bg-cyan-500/10 border-cyan-500/20 text-cyan-500 shadow-inner' : 'border-transparent text-[var(--text-muted)] hover:bg-[var(--hover-bg)] hover:text-[var(--foreground)]'}`}>
                                    <MessageSquare size={14} className={currentChatId === chat.id ? 'text-cyan-500' : 'opacity-40'} />
                                    <span className="truncate flex-1 font-bold uppercase tracking-tight">{chat.title}</span>
                                    <button onClick={(e) => initiateDeleteChat(e, chat.id)} className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 transition-all"><Trash2 size={12} /></button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="p-4 border-t border-[var(--border-color)] space-y-2">
                    <button onClick={() => setShowShortcuts(true)} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-[var(--border-color)] text-[10px] font-black uppercase text-[var(--text-muted)] hover:text-[var(--foreground)] transition-all">
                        <Command size={14} /> Shortcuts
                    </button>
                    <button onClick={() => setShowSettings(true)} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-cyan-500/10 text-[10px] font-black uppercase text-[var(--text-muted)] hover:text-cyan-500 transition-all italic tracking-widest">
                        <Settings size={14} /> AI Settings
                    </button>
                    <button onClick={handleLogout} className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-red-500/10 text-[10px] font-black uppercase text-red-500/60 hover:text-red-500 transition-all italic tracking-widest">
                        <X size={14} /> System Exit
                    </button>
                </div>
            </motion.aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col relative min-w-0 bg-[var(--background)]">
                {/* Header */}
                <header className="h-16 border-b border-[var(--border-color)] flex items-center justify-between px-6 lg:px-10 bg-[var(--background)]/60 backdrop-blur-xl z-20 sticky top-0">
                    <div className="flex items-center gap-4">
                        {!sidebarOpen && (
                            <button onClick={() => setSidebarOpen(true)} className="p-2.5 rounded-xl bg-[var(--card-bg)] border border-[var(--border-color)] text-[var(--text-muted)] hover:text-cyan-500 transition-all shadow-sm">
                                <Menu size={20} />
                            </button>
                        )}
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-black tracking-tight italic opacity-80 uppercase">Intelligence Protocol</span>
                            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <button onClick={toggleTheme} className="p-2.5 rounded-xl border border-[var(--border-color)] text-[var(--text-muted)] hover:text-cyan-500 transition-all">
                            {theme === 'dark' ? <Sparkles size={18} /> : <FileText size={18} />}
                        </button>
                        <div className="hidden sm:flex items-center gap-2.5 px-4 py-2 bg-[var(--sidebar-bg)] border border-[var(--border-color)] rounded-2xl">
                            <span className="text-[9px] font-black text-cyan-500 uppercase tracking-widest italic">TalentPulse Engine</span>
                        </div>
                    </div>
                </header>

                {/* Chat window */}
                <div ref={scrollContainerRef} onScroll={handleScroll} className="flex-1 overflow-y-auto p-4 md:p-10 custom-scrollbar relative">
                    <div className="max-w-4xl mx-auto space-y-12 pb-24">
                        <AnimatePresence mode='popLayout'>
                            {messages.length === 0 && (
                                <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col items-center justify-center py-20 text-center space-y-10">
                                    <div className="w-32 h-32 rounded-[3.5rem] bg-white flex items-center justify-center shadow-[0_20px_60px_rgba(6,182,212,0.15)] relative group overflow-hidden">
                                        <Logo size={100} className="group-hover:scale-110 transition-transform duration-500" />
                                        <div className="absolute inset-0 bg-cyan-400 blur-3xl -z-10 opacity-10 group-hover:opacity-20 transition-opacity" />
                                    </div>
                                    <div className="space-y-4">
                                        <h2 className="text-6xl md:text-7xl font-black tracking-tighter italic uppercase text-[var(--foreground)]">
                                            TALENT<span className="text-cyan-500">PULSE</span>
                                        </h2>
                                        <p className="text-[var(--text-muted)] text-xs font-bold uppercase tracking-[0.5em] opacity-40">Unified Business Intelligence Engine</p>
                                    </div>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl pt-8">
                                        {["Analyze Recent Sales", "Pending Enrollment Audit", "Employee Performance Trend", "Generate Revenue Chart"].map((label, i) => (
                                            <button key={i} onClick={() => sendMessage(label)} className="p-6 rounded-3xl bg-[var(--sidebar-bg)] border border-[var(--border-color)] hover:border-cyan-500 hover:bg-cyan-500/5 transition-all text-left uppercase text-[10px] font-black tracking-widest text-[var(--text-muted)] hover:text-[var(--foreground)]">
                                                {label}
                                            </button>
                                        ))}
                                    </div>
                                </motion.div>
                            )}

                            {messages.map((msg, idx) => (
                                <motion.div key={idx} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`flex max-w-[95%] md:max-w-[85%] gap-5 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 border border-[var(--border-color)] shadow-sm mt-1 overflow-hidden ${msg.role === 'user' ? 'bg-indigo-500/10 text-indigo-500' : 'bg-white'}`}>
                                            {msg.role === 'user' ? <User size={20} /> : <Logo size={28} />}
                                        </div>
                                        <div className={`px-8 py-6 rounded-[2.5rem] text-[15px] leading-8 shadow-sm ${msg.role === 'user' ? 'bg-indigo-500/5 border border-indigo-500/10 text-[var(--foreground)] rounded-tr-sm' : 'bg-[var(--sidebar-bg)] border border-[var(--border-color)] text-[var(--foreground)] rounded-tl-sm shadow-xl'}`}>
                                            <div className="markdown normal-case">
                                                <ReactMarkdown
                                                    remarkPlugins={[remarkGfm]}
                                                    components={{
                                                        code({ node, inline, className, children, ...props }: any) {
                                                            const match = /language-chart-(\w+)/.exec(className || '');
                                                            if (!inline && match) {
                                                                try {
                                                                    const chartData = JSON.parse(String(children).trim());
                                                                    return <ChartRenderer type={match[1]} data={chartData} />;
                                                                } catch (e) {
                                                                    return <code className={className} {...props}>{children}</code>;
                                                                }
                                                            }
                                                            return <code className={className} {...props}>{children}</code>;
                                                        }
                                                    }}
                                                >
                                                    {msg.content}
                                                </ReactMarkdown>
                                            </div>
                                            {msg.role === 'ai' && msg.options && msg.options.length > 0 && (
                                                <div className="mt-8 flex flex-wrap gap-3">
                                                    {msg.options.map((opt, i) => (
                                                        <button
                                                            key={i}
                                                            onClick={() => sendMessage(opt)}
                                                            className="px-6 py-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-500 font-black uppercase text-[10px] tracking-widest hover:bg-cyan-500 hover:text-white transition-all shadow-sm"
                                                        >
                                                            {opt}
                                                        </button>
                                                    ))}
                                                </div>
                                            )}

                                            {msg.role === 'ai' && (
                                                <div className="flex gap-4 mt-6 border-t border-[var(--border-color)] pt-4 opacity-40 hover:opacity-100 transition-opacity">
                                                    <button onClick={() => speak(msg.content)} className="p-2 hover:text-blue-500 transition-colors" title="Listen"><Volume2 size={16} /></button>
                                                    <button onClick={() => downloadReport(msg.content)} className="p-2 hover:text-green-500 transition-colors" title="Export MD"><Download size={16} /></button>
                                                    <button onClick={() => copyToClipboard(msg.content, idx)} className="p-2 hover:text-cyan-500 transition-colors" title="Copy">{copiedIndex === idx ? <Check size={16} /> : <Copy size={16} />}</button>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}

                            {loading && (
                                <div className="flex justify-start pl-16 pt-2">
                                    <div className="flex gap-1.5 p-5 rounded-[1.5rem] bg-[var(--sidebar-bg)] border border-[var(--border-color)] items-center shadow-lg">
                                        <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                                        <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                        <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                                        <span className="text-[10px] font-black uppercase text-cyan-500 ml-3 animate-pulse">Syncing Brain...</span>
                                    </div>
                                </div>
                            )}
                        </AnimatePresence>
                        <div ref={messagesEndRef} />
                    </div>

                    {showScrollBtn && (
                        <button onClick={scrollToBottom} className="fixed bottom-36 right-10 p-4 rounded-full bg-cyan-500 text-white shadow-2xl animate-bounce hover:scale-110 active:scale-95 transition-all">
                            <ArrowDown size={24} />
                        </button>
                    )}
                </div>

                {/* Input bar */}
                <div className="p-6 md:p-10 bg-[var(--background)] border-t border-[var(--border-color)] z-20">
                    <div className="max-w-4xl mx-auto">
                        <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="relative group">
                            <div className="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-40" />
                            <div className="flex items-center bg-[var(--sidebar-bg)] border border-[var(--border-color)] rounded-[2.5rem] shadow-2xl overflow-hidden focus-within:border-cyan-500 transition-all px-2">
                                <div className="pl-6 text-cyan-500/40 group-focus-within:text-cyan-500 group-focus-within:scale-110 transition-all">
                                    <Sparkles size={22} />
                                </div>
                                <button type="button" onClick={() => setShowKB(true)} className="ml-4 p-2 text-slate-400 hover:text-cyan-500 hover:bg-cyan-500/10 rounded-full transition-all" title="Upload Resume">
                                    <Plus size={22} />
                                </button>
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Ask TalentPulse AI about Business Data..."
                                    className="w-full bg-transparent p-7 focus:outline-none text-[var(--foreground)] font-bold text-base placeholder:opacity-30 normal-case"
                                />
                                <button type="submit" disabled={loading || !input.trim()} className="m-2 p-5 rounded-[1.8rem] bg-gradient-to-tr from-cyan-500 to-blue-600 text-white shadow-xl disabled:opacity-30 hover:scale-105 active:scale-95 transition-all">
                                    <Send size={20} />
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </main>
    );
}
