import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import InputForm from './components/InputForm';
import BriefingDisplay from './components/BriefingDisplay';
import SharedBriefing from './pages/SharedBriefing';
import type { Briefing } from './types';

function App() {
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleBriefingGenerated = (newBriefing: Briefing) => {
    setBriefing(newBriefing);
    setLoading(false);
    setError(null);
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setLoading(false);
  };

  const handleReset = () => {
    setBriefing(null);
    setError(null);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/briefing/:id" element={<SharedBriefing />} />
        <Route path="/" element={
          <div className="min-h-screen relative">
            {/* Editorial Grid Lines - Subtle background texture */}
            <div className="fixed inset-0 pointer-events-none opacity-30">
              <div className="absolute left-1/4 top-0 bottom-0 w-px bg-gold/10" />
              <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gold/10" />
              <div className="absolute left-3/4 top-0 bottom-0 w-px bg-gold/10" />
            </div>

            {/* Main Content */}
            <div className="relative z-10">
              {/* Editorial Masthead */}
              <header className="relative pt-16 pb-12 px-6 overflow-hidden">
                {/* Drop number decoration */}
                <div className="drop-number top-0 -left-8 -z-10">01</div>

                <div className="max-w-7xl mx-auto">
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-end">
                    {/* Main title section */}
                    <div className="lg:col-span-8">
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
                        className="space-y-6"
                      >
                        {/* Byline */}
                        <div className="byline text-gold-dark flex items-center gap-3">
                          <span>INTELLIGENCE PLATFORM</span>
                          <div className="w-12 h-px bg-gold" />
                          <span>EST. 2026</span>
                        </div>

                        {/* Main masthead */}
                        <h1 className="text-8xl md:text-9xl leading-none tracking-tighter">
                          <span className="block text-gradient-gold animate-reveal-up">NewsLens</span>
                          <span className="block text-ink animate-reveal-up delay-100">Intelligence</span>
                        </h1>

                        {/* Tagline */}
                        <div className="animate-reveal-up delay-200">
                          <p className="text-2xl md:text-3xl font-display italic text-gray leading-tight max-w-2xl">
                            Transforming business news into actionable intelligence through
                            <span className="text-gold-dark font-bold"> multi-modal analysis</span>
                          </p>
                        </div>

                        {/* Stats bar */}
                        <div className="flex flex-wrap gap-8 pt-4 animate-reveal-up delay-300">
                          <div>
                            <div className="text-4xl font-display font-black text-gold">8×</div>
                            <div className="text-xs uppercase tracking-wider text-gray-light">Faster Reading</div>
                          </div>
                          <div className="w-px bg-ink/10" />
                          <div>
                            <div className="text-4xl font-display font-black text-gold">90%</div>
                            <div className="text-xs uppercase tracking-wider text-gray-light">Consolidation</div>
                          </div>
                          <div className="w-px bg-ink/10" />
                          <div>
                            <div className="text-4xl font-display font-black text-gold">10s</div>
                            <div className="text-xs uppercase tracking-wider text-gray-light">Generation Time</div>
                          </div>
                        </div>
                      </motion.div>
                    </div>

                    {/* Sidebar - Actions and status */}
                    <div className="lg:col-span-4 flex flex-col gap-4">
                      {briefing && (
                        <motion.button
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={handleReset}
                          className="btn-editorial justify-center"
                        >
                          <span>+ NEW BRIEFING</span>
                        </motion.button>
                      )}

                      {/* Live indicator */}
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="editorial-card p-4"
                      >
                        <div className="flex items-center gap-3">
                          <div className="relative">
                            <div className="w-3 h-3 bg-gold rounded-full" />
                            <div className="absolute inset-0 w-3 h-3 bg-gold rounded-full animate-ping" />
                          </div>
                          <div>
                            <div className="text-xs uppercase tracking-wider font-semibold text-ink">System Online</div>
                            <div className="text-xs text-gray-light">Ready for Analysis</div>
                          </div>
                        </div>
                      </motion.div>
                    </div>
                  </div>

                  {/* Decorative rule */}
                  <motion.div
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    transition={{ duration: 1, delay: 0.4 }}
                    className="editorial-rule mt-12 origin-left"
                  />
                </div>
              </header>

              {/* Main Content Area */}
              <main className="px-6 pb-32">
                <div className="max-w-7xl mx-auto">
                  <AnimatePresence mode="wait">
                    {!briefing && !loading ? (
                      <motion.div
                        key="input"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.4 }}
                      >
                        <InputForm
                          onGenerate={handleBriefingGenerated}
                          onLoading={() => setLoading(true)}
                          onError={handleError}
                        />

                        {error && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mt-8 editorial-card border-red/30 p-6"
                          >
                            <div className="flex items-start gap-4">
                              <div className="w-2 h-2 bg-red rounded-full mt-2 flex-shrink-0" />
                              <div>
                                <h3 className="font-display font-bold text-red mb-2">Analysis Error</h3>
                                <p className="text-gray text-sm leading-relaxed">{error}</p>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </motion.div>
                    ) : loading ? (
                      <motion.div
                        key="loading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="py-32"
                      >
                        <div className="max-w-2xl mx-auto text-center space-y-8">
                          {/* Loading spinner */}
                          <div className="relative inline-block">
                            <motion.div
                              animate={{ rotate: 360 }}
                              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                              className="w-32 h-32 border-4 border-cream border-t-gold rounded-full"
                            />
                            <div className="absolute inset-0 flex items-center justify-center">
                              <motion.div
                                animate={{ scale: [1, 1.2, 1] }}
                                transition={{ duration: 2, repeat: Infinity }}
                                className="w-16 h-16 bg-gold/20 rounded-full blur-xl"
                              />
                            </div>
                          </div>

                          {/* Loading text */}
                          <div className="space-y-4">
                            <motion.h2
                              animate={{ opacity: [0.5, 1, 0.5] }}
                              transition={{ duration: 2, repeat: Infinity }}
                              className="font-display text-4xl text-ink"
                            >
                              Analyzing Intelligence
                            </motion.h2>
                            <div className="space-y-2">
                              <div className="byline text-gray">PROCESSING ARTICLES</div>
                              <div className="w-64 h-1 bg-cream mx-auto rounded-full overflow-hidden">
                                <motion.div
                                  animate={{ x: ['-100%', '100%'] }}
                                  transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                                  className="w-1/3 h-full bg-gradient-gold"
                                />
                              </div>
                            </div>
                          </div>

                          {/* Loading steps */}
                          <div className="grid grid-cols-3 gap-4 text-left pt-8">
                            {[
                              { step: '01', label: 'Extracting Entities' },
                              { step: '02', label: 'Building Timeline' },
                              { step: '03', label: 'Generating Insights' },
                            ].map((item, i) => (
                              <motion.div
                                key={item.step}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="editorial-card p-4"
                              >
                                <div className="font-display text-3xl text-gold/30 mb-1">{item.step}</div>
                                <div className="text-xs uppercase tracking-wider text-gray-light">{item.label}</div>
                              </motion.div>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    ) : briefing ? (
                      <motion.div
                        key="briefing"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.6 }}
                      >
                        <BriefingDisplay briefing={briefing} onReset={handleReset} />
                      </motion.div>
                    ) : null}
                  </AnimatePresence>
                </div>
              </main>

              {/* Editorial Footer */}
              <footer className="fixed bottom-0 left-0 right-0 z-50 no-print">
                <div className="glass-editorial border-t-2 border-ink/10">
                  <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between text-sm">
                      <div className="byline text-gray-light">
                        ET AI HACKATHON 2026 · PROBLEM STATEMENT #8
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-gold rounded-full animate-pulse-soft" />
                          <span className="text-gray text-xs">Multi-Modal Intelligence Engine</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </footer>
            </div>
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
