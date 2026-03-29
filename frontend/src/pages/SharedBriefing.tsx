import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import BriefingDisplay from '../components/BriefingDisplay';
import { getBriefing } from '../api/client';
import type { Briefing } from '../types';

const SharedBriefing = () => {
  const { id } = useParams<{ id: string }>();
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadBriefing = async () => {
      if (!id) {
        setError('No briefing ID provided');
        setLoading(false);
        return;
      }

      try {
        const data = await getBriefing(id);
        setBriefing(data);
      } catch (err) {
        setError('Briefing not found');
      } finally {
        setLoading(false);
      }
    };

    loadBriefing();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 border-4 border-navy-700 border-t-amber-500 rounded-full mx-auto"
          />
          <p className="mt-4 text-navy-200">Loading shared briefing...</p>
        </div>
      </div>
    );
  }

  if (error || !briefing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glass-effect p-8 rounded-2xl max-w-md text-center">
          <p className="text-red-300 mb-4">{error || 'Briefing not found'}</p>
          <a href="/" className="text-amber-400 hover:text-amber-300 underline">
            Go to Home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-x-hidden">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-20 left-10 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10">
        <header className="pt-12 pb-8 px-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-5xl font-display font-bold tracking-tight mb-3">
              <span className="gradient-text">NewsLens</span>
              <span className="text-navy-100"> AI</span>
            </h1>
            <p className="text-navy-400 text-sm">Shared Intelligence Briefing</p>
          </div>
        </header>

        <main className="px-6 pb-20">
          <div className="max-w-7xl mx-auto">
            <BriefingDisplay briefing={briefing} onReset={() => window.location.href = '/'} />
          </div>
        </main>
      </div>
    </div>
  );
};

export default SharedBriefing;
