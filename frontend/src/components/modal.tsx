'use client';

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';

export const inputClass =
  'w-full px-4 py-2.5 glass-subtle rounded-xl text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary-500/40 transition-all';
export const selectClass = inputClass + ' [&>option]:bg-white [&>option]:text-slate-900';
export const labelClass = 'block text-sm font-medium text-foreground/80 mb-1.5';

export function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/60" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, y: 16, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        className="w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-3xl p-6 bg-white dark:bg-surface-dark border border-white/10 shadow-elevation-4 text-foreground"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl font-bold text-foreground">{title}</h2>
          <button onClick={onClose} className="p-2 rounded-xl hover:bg-white/10" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>
        {children}
      </motion.div>
    </div>
  );
}