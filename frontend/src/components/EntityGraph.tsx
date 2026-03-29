import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { motion } from 'framer-motion';
import { Network, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

interface Entity {
  name: string;
  type: string;
  context: string;
}

interface Relationship {
  source: string;
  target: string;
  type: string;
  strength: number;
}

interface EntityGraphProps {
  entities: Entity[];
  relationships: Relationship[];
}

interface GraphNode {
  id: string;
  name: string;
  type: string;
  val: number;
  x?: number;
  y?: number;
}

interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  type: string;
  strength: number;
}

const EntityGraph: React.FC<EntityGraphProps> = ({ entities, relationships }) => {
  const graphRef = useRef<any>();
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({
    nodes: [],
    links: []
  });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    // Count entity importance (mentions in relationships)
    const entityImportance = new Map<string, number>();
    relationships.forEach(rel => {
      entityImportance.set(rel.source, (entityImportance.get(rel.source) || 0) + 1);
      entityImportance.set(rel.target, (entityImportance.get(rel.target) || 0) + 1);
    });

    // Find max importance for scaling
    const maxImportance = Math.max(...Array.from(entityImportance.values()), 1);

    // Build graph nodes with size based on importance
    const nodes: GraphNode[] = entities.map(entity => {
      const importance = entityImportance.get(entity.name) || 0;

      // Scale: Most important = size 15, least important = size 6
      const normalizedImportance = maxImportance > 0 ? importance / maxImportance : 0;
      const nodeSize = 6 + (normalizedImportance * 9);

      return {
        id: entity.name,
        name: entity.name,
        type: entity.type,
        val: nodeSize
      };
    });

    setGraphData({
      nodes,
      links: relationships.map(rel => ({
        source: rel.source,
        target: rel.target,
        type: rel.type,
        strength: rel.strength
      }))
    });
  }, [entities, relationships]);

  if (relationships.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="editorial-card p-8 text-center"
      >
        <Network className="w-12 h-12 text-gray mx-auto mb-3" />
        <h3 className="text-lg font-display font-bold text-ink mb-2">
          No Entity Relationships Found
        </h3>
        <p className="text-gray text-sm">
          This article doesn't contain explicit relationships between entities.
        </p>
      </motion.div>
    );
  }

  // Color mapping for entity types with editorial palette
  const getNodeColor = (type: string) => {
    const colors: Record<string, string> = {
      company: '#d4af37',      // Gold
      person: '#b8941f',       // Gold dark
      policy: '#dc2626',       // Red
      organization: '#991b1b', // Red dark
      country: '#d4af37',      // Gold
      technology: '#b8941f',   // Gold dark
      product: '#dc2626'       // Red
    };
    return colors[type] || '#525252'; // Gray fallback
  };

  // Get gradient color for nodes (editorial gold/red)
  const getNodeGradient = (type: string) => {
    const gradients: Record<string, { start: string; end: string }> = {
      company: { start: '#d4af37', end: '#b8941f' },
      person: { start: '#b8941f', end: '#8b7518' },
      policy: { start: '#dc2626', end: '#991b1b' },
      organization: { start: '#991b1b', end: '#7f1d1d' },
      country: { start: '#d4af37', end: '#b8941f' },
      technology: { start: '#b8941f', end: '#8b7518' },
      product: { start: '#dc2626', end: '#991b1b' }
    };
    return gradients[type] || { start: '#525252', end: '#404040' };
  };

  // Relationship type labels
  const getRelationshipLabel = (type: string) => {
    const labels: Record<string, string> = {
      competes_with: 'competes with',
      partners_with: 'partners with',
      invests_in: 'invests in',
      acquires: 'acquires',
      regulates: 'regulates',
      supplies_to: 'supplies to',
      leads: 'leads',
      owns: 'owns',
      supports: 'supports',
      develops: 'develops',
      uses: 'uses'
    };
    return labels[type] || type;
  };

  // Zoom controls
  const handleZoomIn = () => {
    if (graphRef.current) {
      graphRef.current.zoom(graphRef.current.zoom() * 1.5);
    }
  };

  const handleZoomOut = () => {
    if (graphRef.current) {
      graphRef.current.zoom(graphRef.current.zoom() / 1.5);
    }
  };

  const handleZoomFit = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400, 80);
    }
  };

  return (
    <div className="editorial-card p-8 md:p-10">
      {/* Header */}
      <div className="mb-8 pb-6 border-b-2 border-ink/10">
        <div className="byline text-gold-dark mb-3">NETWORK INTELLIGENCE</div>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <Network className="w-8 h-8 text-gold" />
            <div>
              <h3 className="text-3xl font-display font-black text-ink">
                Entity Relationship Network
              </h3>
              <p className="text-sm text-gray mt-1">
                {entities.length} entities • {relationships.length} connections
              </p>
            </div>
          </div>

          {/* Zoom Controls */}
          <div className="flex gap-2">
            <button
              onClick={handleZoomIn}
              className="p-2 bg-cream hover:bg-gold/10 border border-ink/10 transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4 text-ink" />
            </button>
            <button
              onClick={handleZoomOut}
              className="p-2 bg-cream hover:bg-gold/10 border border-ink/10 transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4 text-ink" />
            </button>
            <button
              onClick={handleZoomFit}
              className="p-2 bg-cream hover:bg-gold/10 border border-ink/10 transition-colors"
              title="Fit to View"
            >
              <Maximize2 className="w-4 h-4 text-ink" />
            </button>
          </div>
        </div>
      </div>

      {/* Graph Container */}
      <div className="relative bg-paper rounded-none overflow-hidden border-2 border-ink/10">
        <div className="absolute inset-0 bg-gradient-to-br from-cream/50 to-paper"></div>
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          width={window.innerWidth > 1024 ? 1000 : 800}
          height={650}
          nodeLabel={(node: any) => {
            const entity = entities.find(e => e.name === node.name);
            const importance = node.val > 12 ? '★ Key Player' : node.val > 9 ? '◆ Important' : '○ Supporting';
            return `${importance}\n${node.name}\nType: ${node.type}\n${entity?.context ? '\n' + entity.context.slice(0, 100) + '...' : ''}`;
          }}
          nodeColor={(node: any) => getNodeColor(node.type)}
          nodeRelSize={6}
          nodeVal={(node: any) => node.val}
          nodeCanvasObjectMode={(node: any) => selectedNode?.id === node.id ? 'before' : 'after'}
          nodeCanvasObject={(node: any, ctx: any, globalScale: number) => {
            // Skip rendering if node position isn't set yet
            if (!node.x || !node.y || !isFinite(node.x) || !isFinite(node.y)) {
              return;
            }

            const isSelected = selectedNode?.id === node.id;
            const gradient = getNodeGradient(node.type);

            // Draw glow effect for selected or important nodes
            if (isSelected || node.val > 10) {
              ctx.beginPath();
              ctx.arc(node.x, node.y, node.val * 1.8, 0, 2 * Math.PI);
              const glowGradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.val * 1.8);
              glowGradient.addColorStop(0, isSelected ? getNodeColor(node.type) + '66' : getNodeColor(node.type) + '33');
              glowGradient.addColorStop(1, 'transparent');
              ctx.fillStyle = glowGradient;
              ctx.fill();
            }

            // Draw node with gradient
            const nodeGradient = ctx.createRadialGradient(
              node.x - node.val/3, node.y - node.val/3, 0,
              node.x, node.y, node.val
            );
            nodeGradient.addColorStop(0, gradient.start);
            nodeGradient.addColorStop(1, gradient.end);

            ctx.beginPath();
            ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI);
            ctx.fillStyle = nodeGradient;
            ctx.fill();

            // Draw border
            ctx.strokeStyle = isSelected ? '#0a0a0a' : 'rgba(10, 10, 10, 0.3)';
            ctx.lineWidth = isSelected ? 2 : 1;
            ctx.stroke();

            // Draw label
            const label = node.name;
            const fontSize = Math.max(9, 12/globalScale);
            ctx.font = `600 ${fontSize}px "Instrument Sans", -apple-system, BlinkMacSystemFont, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';

            // Label background for readability
            const labelWidth = ctx.measureText(label).width;
            const labelPadding = 4;
            ctx.fillStyle = 'rgba(253, 251, 247, 0.95)';
            ctx.fillRect(
              node.x - labelWidth/2 - labelPadding,
              node.y + node.val + 3,
              labelWidth + labelPadding * 2,
              fontSize + labelPadding
            );

            // Label text
            ctx.fillStyle = isSelected ? '#0a0a0a' : node.val > 10 ? '#525252' : '#a3a3a3';
            ctx.fillText(label, node.x, node.y + node.val + 6);
          }}
          linkLabel={(link: any) => {
            const sourceName = typeof link.source === 'object' ? link.source.name : link.source;
            const targetName = typeof link.target === 'object' ? link.target.name : link.target;
            return `${sourceName} ${getRelationshipLabel(link.type)} ${targetName}`;
          }}
          linkColor={(link: any) => {
            const alpha = Math.max(0.3, link.strength);
            return `rgba(82, 82, 82, ${alpha})`; // Gray with transparency
          }}
          linkWidth={(link: any) => Math.max(1, link.strength * 2.5)}
          linkDirectionalArrowLength={5}
          linkDirectionalArrowRelPos={0.95}
          linkCurvature={0.15}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.004}
          linkDirectionalParticleWidth={(link: any) => Math.max(1.5, link.strength * 2)}
          linkDirectionalParticleColor={() => '#d4af37'} // Gold particles
          backgroundColor="transparent"
          enableNodeDrag={true}
          enableZoomInteraction={true}
          onNodeClick={(node: any) => setSelectedNode(node)}
          onBackgroundClick={() => setSelectedNode(null)}
          d3VelocityDecay={0.4}
          d3Force="charge"
          d3ForceConfig={{
            charge: { strength: -200, distanceMax: 400 },
            link: { distance: 80 }
          }}
          cooldownTicks={150}
          warmupTicks={100}
          onEngineStop={() => {
            if (graphRef.current) {
              setTimeout(() => {
                graphRef.current.zoomToFit(400, 60);
              }, 100);
            }
          }}
        />
      </div>

      {/* Legend and Info */}
      <div className="mt-6 space-y-4">
        {/* Entity Types Legend */}
        <div className="flex flex-wrap gap-3 items-center">
          <span className="byline text-gray">Entity Types:</span>
          {Array.from(new Set(entities.map(e => e.type))).map(type => (
            <div key={type} className="flex items-center gap-2 px-3 py-1.5 bg-cream border border-ink/10">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: getNodeColor(type) }}
              />
              <span className="text-xs text-ink font-medium capitalize">{type}</span>
            </div>
          ))}
        </div>

        {/* Relationship Types */}
        <div className="flex flex-wrap gap-2 items-center">
          <span className="byline text-gray">Relationships:</span>
          {Array.from(new Set(relationships.map(r => r.type))).map(type => (
            <span key={type} className="tag-editorial text-xs">
              {getRelationshipLabel(type)}
            </span>
          ))}
        </div>

        {/* Selected Node Info */}
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-gold/5 border-2 border-gold/30"
          >
            <div className="flex items-center gap-2 mb-2">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: getNodeColor(selectedNode.type) }}
              />
              <h4 className="text-sm font-display font-bold text-ink">{selectedNode.name}</h4>
              <span className="text-xs px-2 py-0.5 bg-gold/20 text-gold-dark uppercase tracking-wider font-semibold">
                {selectedNode.type}
              </span>
            </div>
            <p className="text-xs text-gray leading-relaxed">
              {entities.find(e => e.name === selectedNode.name)?.context || 'No additional context available'}
            </p>
          </motion.div>
        )}

        {/* Instructions */}
        <div className="text-xs text-gray-light italic border-l-2 border-gold/30 pl-4">
          Drag nodes to rearrange • Click nodes for details • Scroll to zoom • Larger nodes = more connections
        </div>
      </div>
    </div>
  );
};

export default EntityGraph;
