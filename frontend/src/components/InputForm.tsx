import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileUp, Link2, Sparkles, ArrowRight, Network, Loader2, Check } from 'lucide-react';
import { generateBriefing, findRelatedArticles, type RelatedArticle } from '../api/client';
import type { Briefing } from '../types';

interface InputFormProps {
  onGenerate: (briefing: Briefing) => void;
  onLoading: () => void;
  onError: (error: string) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onGenerate, onLoading, onError }) => {
  const [urls, setUrls] = useState<string>('');
  const [mode, setMode] = useState<'urls' | 'upload'>('urls');
  const [isDiscovering, setIsDiscovering] = useState<boolean>(false);
  const [relatedArticles, setRelatedArticles] = useState<RelatedArticle[]>([]);
  const [selectedArticles, setSelectedArticles] = useState<Set<string>>(new Set());

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!urls.trim()) {
      onError('Please enter at least one article URL');
      return;
    }

    const lines = urls.split('\n').map(line => line.trim()).filter(line => line.length > 0);

    let urlList: string[] = [];
    let currentUrl = '';

    for (const line of lines) {
      if (line.startsWith('http://') || line.startsWith('https://')) {
        if (currentUrl) {
          urlList.push(currentUrl);
        }
        currentUrl = line;
      } else {
        currentUrl += line;
      }
    }

    if (currentUrl) {
      urlList.push(currentUrl);
    }

    if (urlList.length === 0) {
      const singleUrl = urls.replace(/\s+/g, '').trim();
      if (singleUrl.length > 0 && (singleUrl.startsWith('http://') || singleUrl.startsWith('https://'))) {
        urlList = [singleUrl];
      }
    }

    if (urlList.length === 0) {
      onError('Please enter valid article URLs');
      return;
    }

    onLoading();

    try {
      const briefing = await generateBriefing({ article_urls: urlList });
      onGenerate(briefing);
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to generate briefing. Please try again.');
    }
  };

  const exampleUrls = [
    'https://economictimes.indiatimes.com/news/economy/policy/union-budget-2026',
    'https://economictimes.indiatimes.com/markets/stocks/earnings/q4-results',
    'https://economictimes.indiatimes.com/news/economy/policy/rbi-monetary-policy'
  ];

  const loadExample = () => {
    setUrls(exampleUrls.join('\n'));
  };

  const handleDiscoverRelated = async () => {
    const firstUrl = urls.split('\n')[0].trim();

    if (!firstUrl || (!firstUrl.startsWith('http://') && !firstUrl.startsWith('https://'))) {
      onError('Please enter a valid URL first');
      return;
    }

    setIsDiscovering(true);
    setRelatedArticles([]);
    setSelectedArticles(new Set());

    try {
      const related = await findRelatedArticles(firstUrl);
      setRelatedArticles(related);
      setSelectedArticles(new Set(related.map(a => a.url)));
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to find related articles. Please try again.');
      setRelatedArticles([]);
    } finally {
      setIsDiscovering(false);
    }
  };

  const toggleArticleSelection = (url: string) => {
    const newSelected = new Set(selectedArticles);
    if (newSelected.has(url)) {
      newSelected.delete(url);
    } else {
      newSelected.add(url);
    }
    setSelectedArticles(newSelected);
  };

  const addSelectedArticles = () => {
    const currentUrls = urls.split('\n').map(u => u.trim()).filter(u => u.length > 0);
    const newUrls = Array.from(selectedArticles).filter(url => !currentUrls.includes(url));
    const allUrls = [...currentUrls, ...newUrls];
    setUrls(allUrls.join('\n'));
    setRelatedArticles([]);
    setSelectedArticles(new Set());
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Mode Selector */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex gap-4 mb-8"
      >
        <button
          onClick={() => setMode('urls')}
          className={`flex-1 flex items-center justify-center gap-3 px-8 py-5 font-body font-semibold uppercase tracking-wider text-sm transition-all border-2 ${
            mode === 'urls'
              ? 'bg-gold text-ink border-gold-dark shadow-gold'
              : 'bg-white text-gray border-ink/10 hover:border-gold/50'
          }`}
        >
          <Link2 className="w-5 h-5" />
          <span>Paste URLs</span>
        </button>
        <button
          onClick={() => setMode('upload')}
          className={`flex-1 flex items-center justify-center gap-3 px-8 py-5 font-body font-semibold uppercase tracking-wider text-sm transition-all border-2 ${
            mode === 'upload'
              ? 'bg-gold text-ink border-gold-dark shadow-gold'
              : 'bg-white text-gray border-ink/10 hover:border-gold/50'
          }`}
        >
          <FileUp className="w-5 h-5" />
          <span>Upload PDFs</span>
        </button>
      </motion.div>

      {/* Main Form */}
      <motion.form
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        onSubmit={handleSubmit}
        className="editorial-card p-10 md:p-12"
      >
        {/* Form Header */}
        <div className="mb-10 pb-8 border-b-2 border-ink/10">
          <div className="byline text-gold-dark mb-4">INTELLIGENCE INPUT</div>
          <div className="flex items-center gap-4 mb-4">
            <Sparkles className="w-10 h-10 text-gold" />
            <h2 className="text-4xl font-display font-black text-ink">
              Generate Briefing
            </h2>
          </div>
          <p className="text-gray leading-relaxed text-lg">
            Transform multiple news articles into a comprehensive intelligence briefing with visualizations, entity analysis, and audio narration.
          </p>
        </div>

        {mode === 'urls' ? (
          <div className="space-y-6">
            {/* URL Input */}
            <div>
              <label htmlFor="urls" className="block byline text-ink mb-4">
                ARTICLE URLS <span className="text-gray-light">(ONE PER LINE)</span>
              </label>
              <textarea
                id="urls"
                value={urls}
                onChange={(e) => setUrls(e.target.value)}
                placeholder="https://economictimes.indiatimes.com/article1&#10;https://economictimes.indiatimes.com/article2&#10;https://economictimes.indiatimes.com/article3"
                rows={8}
                className="w-full px-6 py-5 bg-cream border-2 border-ink/20 text-ink placeholder-gray-light focus:outline-none focus:border-gold focus:ring-4 focus:ring-gold/10 transition-all font-mono text-sm resize-none"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between flex-wrap gap-4">
              <button
                type="button"
                onClick={loadExample}
                className="text-sm text-gold-dark hover:text-gold underline decoration-dotted underline-offset-4 font-medium uppercase tracking-wider"
              >
                Load Example URLs
              </button>

              {urls.trim().length > 0 && (
                <motion.button
                  type="button"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  onClick={handleDiscoverRelated}
                  disabled={isDiscovering}
                  className="flex items-center gap-2 px-5 py-3 bg-ink text-paper font-semibold uppercase tracking-wider text-xs border-2 border-ink hover:bg-gold hover:text-ink hover:border-gold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isDiscovering ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Discovering...</span>
                    </>
                  ) : (
                    <>
                      <Network className="w-4 h-4" />
                      <span>Find Related Articles</span>
                    </>
                  )}
                </motion.button>
              )}
            </div>

            {/* Related Articles Display */}
            <AnimatePresence>
              {relatedArticles.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="pt-6 border-t-2 border-ink/10 space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="byline text-gold-dark mb-1">RELATED ARTICLES</div>
                      <h3 className="text-xl font-display font-bold text-ink">
                        Found {relatedArticles.length} relevant articles
                      </h3>
                    </div>
                    <button
                      type="button"
                      onClick={addSelectedArticles}
                      disabled={selectedArticles.size === 0}
                      className="flex items-center gap-2 px-5 py-3 bg-gold text-ink font-semibold uppercase tracking-wider text-xs border-2 border-gold-dark hover:bg-gold-dark transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Check className="w-4 h-4" />
                      Add {selectedArticles.size} Selected
                    </button>
                  </div>

                  <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                    {relatedArticles.map((article, idx) => (
                      <motion.div
                        key={article.url}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        onClick={() => toggleArticleSelection(article.url)}
                        className={`p-4 border-2 cursor-pointer transition-all ${
                          selectedArticles.has(article.url)
                            ? 'border-gold bg-gold/5'
                            : 'border-ink/10 bg-white hover:border-gold/30'
                        }`}
                      >
                        <div className="flex items-start gap-4">
                          <div className={`mt-1 w-6 h-6 border-2 flex items-center justify-center transition-all ${
                            selectedArticles.has(article.url)
                              ? 'border-gold bg-gold'
                              : 'border-ink/30'
                          }`}>
                            {selectedArticles.has(article.url) && (
                              <Check className="w-4 h-4 text-ink" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-2">
                              <h4 className="text-sm font-semibold text-ink font-body truncate">
                                {article.title}
                              </h4>
                              <span className={`flex-shrink-0 tag-editorial text-xs ${
                                article.similarity >= 0.5
                                  ? 'bg-gold/20 text-gold-dark border-gold/40'
                                  : article.similarity >= 0.35
                                  ? 'bg-gray/10 text-gray border-gray/30'
                                  : 'bg-ink/5 text-gray-light border-ink/20'
                              }`}>
                                {Math.round(article.similarity * 100)}% MATCH
                              </span>
                            </div>
                            <p className="text-xs text-gray leading-relaxed line-clamp-2">
                              {article.text_preview}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ) : (
          <div>
            <label className="block byline text-ink mb-4">
              UPLOAD PDF ARTICLES
            </label>
            <div className="border-4 border-dashed border-ink/20 p-16 text-center hover:border-gold/50 transition-colors cursor-pointer bg-cream/50">
              <FileUp className="w-16 h-16 text-gray-light mx-auto mb-4" />
              <p className="text-gray font-body text-lg mb-2">Drop PDF files here or click to browse</p>
              <p className="text-sm text-gray-light uppercase tracking-wide">Maximum 10 files • 5MB each</p>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full mt-10 btn-editorial justify-center py-6 text-base group"
        >
          <span>Generate Intelligence Briefing</span>
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>

        {/* Features List */}
        <div className="mt-8 pt-8 border-t-2 border-ink/10">
          <div className="grid grid-cols-3 gap-6 text-center">
            <div>
              <div className="text-3xl font-display font-black text-gold mb-2">8×</div>
              <div className="text-xs uppercase tracking-wider text-gray-light">Faster Reading</div>
            </div>
            <div>
              <div className="text-3xl font-display font-black text-gold mb-2">90%</div>
              <div className="text-xs uppercase tracking-wider text-gray-light">Consolidation</div>
            </div>
            <div>
              <div className="text-3xl font-display font-black text-gold mb-2">10s</div>
              <div className="text-xs uppercase tracking-wider text-gray-light">Generation</div>
            </div>
          </div>
        </div>
      </motion.form>
    </div>
  );
};

export default InputForm;
