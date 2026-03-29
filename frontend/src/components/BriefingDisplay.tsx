import { useState } from 'react';
import { motion } from 'framer-motion';
import { FileText, Lightbulb, BarChart3, AudioLines, RefreshCw, Share2, Download, MessageCircle } from 'lucide-react';
import VisualizationGrid from './VisualizationGrid';
import AudioPlayer from './AudioPlayer';
import EntityGraph from './EntityGraph';
import QAChat from './QAChat';
import type { Briefing } from '../types';
import { saveBriefing, exportBriefingPDF } from '../api/client';

interface BriefingDisplayProps {
  briefing: Briefing;
  onReset: () => void;
}

const BriefingDisplay: React.FC<BriefingDisplayProps> = ({ briefing, onReset }) => {
  const [shareMessage, setShareMessage] = useState<string>('');

  const handleShare = async () => {
    try {
      const { briefing_id } = await saveBriefing(briefing);
      const shareUrl = `${window.location.origin}/briefing/${briefing_id}`;
      await navigator.clipboard.writeText(shareUrl);
      setShareMessage('Link copied to clipboard!');
      setTimeout(() => setShareMessage(''), 3000);
    } catch (error) {
      console.error('Share failed:', error);
      setShareMessage('Failed to create share link');
      setTimeout(() => setShareMessage(''), 3000);
    }
  };

  const handleExport = async () => {
    try {
      setShareMessage('Generating PDF...');
      const pdfBlob = await exportBriefingPDF(briefing);
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `briefing_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      setShareMessage('PDF downloaded successfully!');
      setTimeout(() => setShareMessage(''), 3000);
    } catch (error) {
      console.error('Export failed:', error);
      setShareMessage('Failed to export PDF');
      setTimeout(() => setShareMessage(''), 3000);
    }
  };

  const wordCount = briefing.summary.split(' ').length;
  const readTime = Math.ceil(wordCount / 200);

  return (
    <div className="space-y-16 relative">
      {/* Share Notification */}
      {shareMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="fixed top-6 right-6 z-50 editorial-card border-gold p-4 shadow-gold"
        >
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-gold rounded-full" />
            <span className="font-semibold text-ink">{shareMessage}</span>
          </div>
        </motion.div>
      )}

      {/* Action Bar */}
      <div className="flex items-center justify-between pb-8 border-b-2 border-ink/10">
        <div>
          <div className="byline text-gold-dark mb-2">INTELLIGENCE BRIEFING</div>
          <h2 className="text-5xl font-display font-black text-ink">
            Analysis Complete
          </h2>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleShare}
            className="btn-editorial"
          >
            <Share2 className="w-4 h-4" />
            <span>Share</span>
          </button>
          <button
            onClick={handleExport}
            className="btn-editorial"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Section 02: Executive Summary */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="relative"
      >
        <div className="drop-number top-0 -left-8">02</div>
        <div className="magazine-grid">
          <div className="col-span-12 lg:col-span-8 lg:col-start-3">
            <div className="editorial-card p-8 md:p-12">
              {/* Section header */}
              <div className="mb-8 pb-6 border-b-2 border-ink/10">
                <div className="byline text-gold-dark mb-3">EXECUTIVE SUMMARY</div>
                <div className="flex items-center justify-between">
                  <FileText className="w-8 h-8 text-gold" />
                  <div className="tag-editorial">{readTime} MIN READ</div>
                </div>
              </div>

              {/* Summary text - editorial style */}
              <div className="prose prose-lg max-w-none">
                <p className="text-gray text-xl leading-editorial font-body" style={{ lineHeight: '1.8' }}>
                  {briefing.summary}
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* Decorative rule */}
      <div className="editorial-rule mx-auto max-w-3xl" />

      {/* Section 03: Key Points */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="relative"
      >
        <div className="drop-number top-0 -right-8">03</div>
        <div className="magazine-grid">
          <div className="col-span-12 lg:col-span-10 lg:col-start-2">
            <div className="editorial-card p-8 md:p-12">
              {/* Section header */}
              <div className="mb-10 pb-6 border-b-2 border-ink/10">
                <div className="byline text-gold-dark mb-3">ESSENTIAL INSIGHTS</div>
                <div className="flex items-center justify-between">
                  <h3 className="text-4xl font-display font-black text-ink">
                    What You Need to Know
                  </h3>
                  <div className="tag-editorial">{briefing.key_points.length} POINTS</div>
                </div>
              </div>

              {/* Key points - magazine style */}
              <div className="space-y-6">
                {briefing.key_points.map((point, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + index * 0.05 }}
                    className="flex gap-6 items-start group"
                  >
                    {/* Number badge - editorial style */}
                    <div className="flex-shrink-0 w-12 h-12 bg-gold text-ink rounded-none flex items-center justify-center font-display font-black text-xl border-2 border-ink/10 group-hover:bg-gold-dark group-hover:border-gold transition-all">
                      {String(index + 1).padStart(2, '0')}
                    </div>
                    {/* Point text */}
                    <p className="text-gray text-lg leading-relaxed pt-2 font-body">
                      {point}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* Section 04: Cross-Article Insights */}
      {(briefing.insights.contradictions?.length || briefing.insights.consensus?.length) && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="relative"
        >
          <div className="drop-number top-0 -left-8">04</div>
          <div className="magazine-grid">
            <div className="col-span-12">
              <div className="editorial-card p-8 md:p-12">
                {/* Section header */}
                <div className="mb-10 pb-6 border-b-2 border-ink/10">
                  <div className="byline text-gold-dark mb-3">CROSS-ARTICLE ANALYSIS</div>
                  <div className="flex items-center gap-4">
                    <BarChart3 className="w-8 h-8 text-gold" />
                    <h3 className="text-4xl font-display font-black text-ink">
                      Key Insights
                    </h3>
                  </div>
                </div>

                {/* Insights grid */}
                <div className="grid md:grid-cols-2 gap-8">
                  {/* Contradictions */}
                  {briefing.insights.contradictions && briefing.insights.contradictions.length > 0 && (
                    <div className="editorial-card border-red/30 bg-red/5 p-6">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="w-3 h-3 bg-red rounded-full" />
                        <h4 className="font-display text-xl font-bold text-red-dark uppercase tracking-wide">
                          Contradictions
                        </h4>
                      </div>
                      <ul className="space-y-4">
                        {briefing.insights.contradictions.map((item, idx) => (
                          <li key={idx} className="text-gray text-sm leading-relaxed pl-4 border-l-4 border-red/50">
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Consensus */}
                  {briefing.insights.consensus && briefing.insights.consensus.length > 0 && (
                    <div className="editorial-card border-gold/30 bg-gold/5 p-6">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="w-3 h-3 bg-gold rounded-full" />
                        <h4 className="font-display text-xl font-bold text-gold-dark uppercase tracking-wide">
                          Key Facts
                        </h4>
                      </div>
                      <ul className="space-y-4">
                        {briefing.insights.consensus.map((item, idx) => (
                          <li key={idx} className="text-gray text-sm leading-relaxed pl-4 border-l-4 border-gold/50">
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </motion.section>
      )}

      {/* Section 05: Visualizations */}
      {briefing.visualizations && briefing.visualizations.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="relative"
        >
          <div className="drop-number top-0 -right-8">05</div>
          <div className="mb-8">
            <div className="byline text-gold-dark mb-3">VISUAL INTELLIGENCE</div>
            <h3 className="text-4xl font-display font-black text-ink">
              Data Visualizations
            </h3>
          </div>
          <VisualizationGrid visualizations={briefing.visualizations} />
        </motion.section>
      )}

      {/* Section 06: Entity Relationship Graph */}
      {briefing.entity_graph && briefing.entity_graph.relationships && briefing.entity_graph.relationships.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="relative"
        >
          <div className="drop-number top-0 -left-8">06</div>
          <EntityGraph
            entities={briefing.entity_graph.entities}
            relationships={briefing.entity_graph.relationships}
          />
        </motion.section>
      )}

      {/* Decorative rule */}
      <div className="editorial-rule mx-auto max-w-3xl" />

      {/* Section 07: Audio Briefing */}
      {briefing.audio_url && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="relative"
        >
          <div className="drop-number top-0 -right-8">07</div>
          <div className="magazine-grid">
            <div className="col-span-12 lg:col-span-8 lg:col-start-3">
              <div className="editorial-card border-gold/30 p-8 md:p-10">
                {/* Section header */}
                <div className="mb-8 pb-6 border-b-2 border-ink/10">
                  <div className="byline text-gold-dark mb-3">AUDIO INTELLIGENCE</div>
                  <div className="flex items-center gap-4">
                    <AudioLines className="w-8 h-8 text-gold" />
                    <div>
                      <h3 className="text-3xl font-display font-black text-ink">
                        Listen to Briefing
                      </h3>
                      <p className="text-gray-light text-sm mt-1">Perfect for commuting</p>
                    </div>
                  </div>
                </div>
                <AudioPlayer audioUrl={briefing.audio_url} />
              </div>
            </div>
          </div>
        </motion.section>
      )}

      {/* Section 08: Strategic Questions */}
      {briefing.questions && briefing.questions.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="relative"
        >
          <div className="drop-number top-0 -left-8">08</div>
          <div className="magazine-grid">
            <div className="col-span-12 lg:col-span-10 lg:col-start-2">
              <div className="editorial-card p-8 md:p-12 bg-cream/50">
                {/* Section header */}
                <div className="mb-10 pb-6 border-b-2 border-ink/10">
                  <div className="byline text-gold-dark mb-3">STRATEGIC QUESTIONS</div>
                  <div className="flex items-center gap-4">
                    <MessageCircle className="w-8 h-8 text-gold" />
                    <h3 className="text-4xl font-display font-black text-ink">
                      Questions to Consider
                    </h3>
                  </div>
                </div>

                {/* Questions list */}
                <div className="space-y-4">
                  {briefing.questions.map((question, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.8 + index * 0.05 }}
                      className="flex gap-4 items-start hover:bg-white/50 p-4 -mx-4 rounded transition-colors"
                    >
                      <div className="text-gold-dark font-display text-xl font-bold flex-shrink-0">
                        Q{index + 1}
                      </div>
                      <p className="text-gray font-body text-base leading-relaxed italic">
                        {question}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </motion.section>
      )}

      {/* Section 09: Q&A Chat */}
      {briefing.session_id && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="relative"
        >
          <div className="drop-number top-0 -right-8">09</div>
          <QAChat sessionId={briefing.session_id} />
        </motion.section>
      )}

      {/* End mark - editorial flourish */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="flex items-center justify-center gap-4 py-12"
      >
        <div className="w-12 h-px bg-gold" />
        <div className="font-display text-3xl text-gold">◆</div>
        <div className="w-12 h-px bg-gold" />
      </motion.div>
    </div>
  );
};

export default BriefingDisplay;
