import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BarChart3, TrendingUp, Network, Clock } from 'lucide-react';

interface VisualizationGridProps {
  visualizations: string[];
}

const VisualizationGrid: React.FC<VisualizationGridProps> = ({ visualizations }) => {
  const [activeTab, setActiveTab] = useState(0);

  const vizTypes = [
    { icon: Clock, label: 'Timeline', color: 'gold' },
    { icon: BarChart3, label: 'Comparison', color: 'red' },
    { icon: TrendingUp, label: 'Trends', color: 'gold-dark' },
    { icon: Network, label: 'Network', color: 'red-dark' },
  ];

  return (
    <div className="editorial-card p-8 md:p-10">
      {/* Header */}
      <div className="mb-8 pb-6 border-b-2 border-ink/10">
        <div className="byline text-gold-dark mb-3">VISUAL INTELLIGENCE</div>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <BarChart3 className="w-8 h-8 text-gold" />
            <h3 className="text-3xl font-display font-black text-ink">
              Interactive Visualizations
            </h3>
          </div>
          <div className="tag-editorial">
            {visualizations.length} {visualizations.length === 1 ? 'Chart' : 'Charts'}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {visualizations.map((_, index) => {
          const vizType = vizTypes[index % vizTypes.length];
          const Icon = vizType.icon;
          return (
            <motion.button
              key={index}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setActiveTab(index)}
              className={`flex items-center gap-2 px-5 py-3 font-body font-semibold uppercase tracking-wider text-xs whitespace-nowrap transition-all border-2 ${
                activeTab === index
                  ? 'bg-gold text-ink border-gold-dark'
                  : 'bg-white text-gray border-ink/10 hover:border-gold/50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{vizType.label}</span>
            </motion.button>
          );
        })}
      </div>

      {/* Visualization Display */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="bg-cream border-2 border-ink/10 p-6"
        >
          {/* Render the actual visualization HTML/JSX */}
          <div
            className="w-full min-h-[400px]"
            dangerouslySetInnerHTML={{ __html: visualizations[activeTab] }}
          />
        </motion.div>
      </AnimatePresence>

      {/* Chart Info */}
      <div className="mt-6 pt-6 border-t-2 border-ink/10">
        <div className="flex items-center justify-between text-sm flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-gold rounded-full animate-pulse-soft" />
            <span className="text-gray font-medium">Auto-generated in 10 seconds</span>
          </div>
          <div className="flex gap-4">
            <button className="text-gray hover:text-ink transition-colors font-medium uppercase text-xs tracking-wider">
              Export PNG
            </button>
            <button className="text-gray hover:text-ink transition-colors font-medium uppercase text-xs tracking-wider">
              View Code
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualizationGrid;
