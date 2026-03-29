"""
Agent 2: Visual Intelligence Agent
====================================

Generates dynamic React Artifact visualizations from structured insights.
Outputs: Interactive charts, timelines, and dashboards using Recharts.
"""

import os
from typing import Dict, Any, List
from langchain_aws import ChatBedrock


# ============================================================================
# Visual Intelligence Agent
# ============================================================================

class VisualIntelligenceAgent:
    """
    Agent 2: Generates dynamic visualizations from insights.

    Analyzes structured data and creates appropriate React Artifact code
    using Recharts library for interactive visualizations.
    """

    def __init__(self):
        """Initialize the agent with Claude API client"""
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            model_kwargs={
                "temperature": 0.1,
                "max_tokens": 4096
            }
        )

    def detect_visualization_type(self, insights: Dict[str, Any]) -> str:
        """
        Detect the most appropriate visualization type for the insights.

        Args:
            insights: Structured insights from Agent 1

        Returns:
            Visualization type: timeline, comparison, metrics, network, trend
        """

        prompt = f"""
Analyze the following structured insights and determine the BEST visualization type.

Insights:
- Entities: {len(insights.get('entities', []))} items
- Timeline: {len(insights.get('timeline', []))} events
- Key Metrics: {len(insights.get('key_metrics', {}))} metrics
- Theme: {insights.get('main_theme', 'N/A')}

Choose ONE visualization type:
1. **timeline** - For chronological events, dates, sequences
2. **comparison** - For comparing multiple entities or metrics
3. **metrics** - For displaying key numbers and statistics
4. **network** - For relationships between entities
5. **trend** - For data trends over time

Respond with ONLY the visualization type (one word).
"""

        response = self.llm.invoke(prompt)
        viz_type = response.content.strip().lower()

        # Validate and default to metrics if invalid
        valid_types = ["timeline", "comparison", "metrics", "network", "trend"]
        return viz_type if viz_type in valid_types else "metrics"

    def generate_artifact_code(self, viz_type: str, insights: Dict[str, Any]) -> str:
        """
        Generate React Artifact code for the visualization.

        Args:
            viz_type: Type of visualization to generate
            insights: Structured insights to visualize

        Returns:
            React JSX code as string
        """

        # ALWAYS use templates for reliability - LLM-generated HTML is unreliable
        # The templates are already beautiful and tested
        print(f"🎨 Generating {viz_type} visualization using template")
        return self.get_fallback_template(viz_type, insights)

    def get_fallback_template(self, viz_type: str, insights: Dict[str, Any]) -> str:
        """
        Provide fallback template for visualization.

        Args:
            viz_type: Type of visualization
            insights: Structured insights

        Returns:
            React JSX template as string
        """

        if viz_type == "timeline":
            return self._timeline_template(insights)
        elif viz_type == "comparison":
            return self._comparison_template(insights)
        elif viz_type == "metrics":
            return self._metrics_template(insights)
        elif viz_type == "network":
            return self._network_template(insights)
        elif viz_type == "trend":
            return self._trend_template(insights)
        else:
            return self._metrics_template(insights)

    def _get_visualization_prompt(self, viz_type: str, insights: Dict[str, Any]) -> str:
        """Generate visualization creation prompt"""
        return f"""
Generate a beautiful, interactive React component using Recharts for a {viz_type} visualization.

Data to visualize:
{insights}

Requirements:
1. Use Recharts library components (LineChart, BarChart, PieChart, etc.)
2. Include ResponsiveContainer for mobile-friendly design
3. Add proper axis labels, legends, and tooltips
4. Use a modern color scheme (blues, teals, purples)
5. Make it visually appealing with smooth animations
6. Include className="w-full h-96" for proper sizing

Generate ONLY the JSX code (no imports, no explanations).
Start with <div className="w-full h-96">
"""

    def _timeline_template(self, insights: Dict[str, Any]) -> str:
        """Modern timeline visualization template"""
        timeline_data = insights.get('timeline', [])

        if not timeline_data:
            return '''<div style="width: 100%; min-height: 400px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); border-radius: 1rem;">
  <div style="text-align: center;">
    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; color: #475569;">No Timeline Data</div>
    <div style="font-size: 0.875rem; color: #94a3b8;">Timeline events will appear here</div>
  </div>
</div>'''

        timeline_html = []
        for idx, event in enumerate(timeline_data[:8]):
            date = event.get('date', 'N/A')
            event_text = event.get('event', 'Event description')
            impact = event.get('impact', 'Medium')

            # Modern color scheme
            if impact.lower() == 'high':
                impact_color = '#dc2626'
                bg_color = '#fee2e2'
                badge_color = '#991b1b'
            elif impact.lower() == 'medium':
                impact_color = '#f59e0b'
                bg_color = '#fef3c7'
                badge_color = '#d97706'
            else:
                impact_color = '#10b981'
                bg_color = '#d1fae5'
                badge_color = '#059669'

            is_even = idx % 2 == 0

            timeline_html.append(f'''
      <div style="position: relative; padding-left: {4 if is_even else 2}rem; padding-right: {2 if is_even else 4}rem; margin-bottom: 2rem;">
        {'' if idx == 0 else '<div style="position: absolute; left: 2rem; top: -2rem; width: 2px; height: 2rem; background: linear-gradient(to bottom, #cbd5e1, #e2e8f0);"></div>'}
        <div style="position: absolute; left: 1.5rem; top: 0; width: 1rem; height: 1rem; background: {impact_color}; border-radius: 50%; box-shadow: 0 0 0 4px {bg_color}, 0 0 12px {impact_color}66;"></div>
        <div style="background: white; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 4px solid {impact_color}; position: relative; transition: all 0.3s;">
          <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
            <div style="flex: 1;">
              <div style="display: inline-block; background: {bg_color}; color: {badge_color}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
                {date}
              </div>
              <div style="font-weight: 600; color: #111827; font-size: 1rem; line-height: 1.5;">
                {event_text}
              </div>
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="background: linear-gradient(135deg, {impact_color}22, {impact_color}11); color: {impact_color}; padding: 0.375rem 0.75rem; border-radius: 0.5rem; font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; gap: 0.25rem;">
              {impact} Impact
            </div>
          </div>
        </div>
      </div>''')

        return f'''<div style="width: 100%; min-height: 500px; overflow-y: auto; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); border-radius: 1rem; padding: 2rem; position: relative;">
  <div style="margin-bottom: 2.5rem; text-align: center;">
    <div style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 0.75rem 2rem; border-radius: 9999px; box-shadow: 0 8px 16px rgba(59,130,246,0.3);">
      <div style="font-size: 1.5rem; font-weight: 800; color: white; letter-spacing: 0.025em;">Event Timeline</div>
    </div>
  </div>
  <div style="position: relative;">
    <div style="position: absolute; left: 2rem; top: 1rem; bottom: 1rem; width: 2px; background: linear-gradient(to bottom, #cbd5e1, #e2e8f0, #cbd5e1);"></div>
    {''.join(timeline_html)}
  </div>
</div>'''

    def _comparison_template(self, insights: Dict[str, Any]) -> str:
        """Modern entity cards visualization template"""
        entities = insights.get('entities', [])
        theme = insights.get('main_theme', 'Article Analysis')

        if not entities:
            return '''<div style="width: 100%; min-height: 400px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); border-radius: 1rem;">
  <div style="text-align: center;">
    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; color: #475569;">No Entity Data</div>
    <div style="font-size: 0.875rem; color: #94a3b8;">Entity analysis will appear here</div>
  </div>
</div>'''

        # Group entities by type
        entity_groups = {}
        for entity in entities:
            entity_type = entity.get('type', 'other')
            if entity_type not in entity_groups:
                entity_groups[entity_type] = []
            entity_groups[entity_type].append(entity)

        colors = {
            'company': {'primary': '#3b82f6', 'light': '#dbeafe', 'dark': '#1e40af'},
            'person': {'primary': '#8b5cf6', 'light': '#ede9fe', 'dark': '#6d28d9'},
            'policy': {'primary': '#10b981', 'light': '#d1fae5', 'dark': '#059669'},
            'organization': {'primary': '#f59e0b', 'light': '#fef3c7', 'dark': '#d97706'},
            'country': {'primary': '#06b6d4', 'light': '#cffafe', 'dark': '#0e7490'},
            'technology': {'primary': '#ec4899', 'light': '#fce7f3', 'dark': '#be185d'},
            'product': {'primary': '#14b8a6', 'light': '#ccfbf1', 'dark': '#0f766e'},
            'other': {'primary': '#6b7280', 'light': '#f3f4f6', 'dark': '#374151'}
        }

        # Create entity cards
        entity_html = []
        for entity_type, group_entities in entity_groups.items():
            color_cfg = colors.get(entity_type, colors['other'])

            # Type header
            # Fix pluralization
            type_label = entity_type + ('ies' if entity_type == 'compan' else 's')

            entity_html.append(f'''
    <div style="margin-bottom: 2.5rem;">
      <div style="display: inline-flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; background: linear-gradient(135deg, {color_cfg['primary']}, {color_cfg['dark']}); padding: 0.75rem 1.5rem; border-radius: 9999px; box-shadow: 0 6px 12px {color_cfg['primary']}44;">
        <h3 style="font-weight: 700; color: white; font-size: 1.125rem; text-transform: capitalize; margin: 0;">{type_label}</h3>
        <span style="background: rgba(255,255,255,0.25); color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; border: 1px solid rgba(255,255,255,0.3);">{len(group_entities)}</span>
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.25rem;">''')

            # Entity cards
            for idx, entity in enumerate(group_entities[:8]):
                name = entity.get('name', 'Unknown')
                context = entity.get('context', 'No additional context available')

                # Clean context
                context = context.rstrip('.')
                if not context.endswith('.'):
                    context = context + '.'

                # Alternating subtle animations
                delay = idx * 0.05

                entity_html.append(f'''
        <div style="background: white; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 4px solid {color_cfg['primary']}; position: relative; overflow: hidden; transition: all 0.3s;">
          <div style="position: absolute; top: -30px; right: -30px; width: 80px; height: 80px; background: {color_cfg['light']}; border-radius: 50%; opacity: 0.4;"></div>
          <div style="position: relative; z-index: 1;">
            <div style="margin-bottom: 1rem;">
              <div style="font-weight: 700; color: #0f172a; font-size: 1rem; line-height: 1.3; margin-bottom: 0.5rem;">{name}</div>
              <div style="display: inline-block; background: {color_cfg['light']}; color: {color_cfg['dark']}; padding: 0.125rem 0.5rem; border-radius: 0.375rem; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">{entity_type}</div>
            </div>
            <div style="color: #475569; font-size: 0.875rem; line-height: 1.6;">{context}</div>
            <div style="margin-top: 1rem; height: 2px; width: 100%; background: linear-gradient(to right, {color_cfg['primary']}44, transparent); border-radius: 9999px;"></div>
          </div>
        </div>''')

            entity_html.append('''
      </div>
    </div>''')

        return f'''<div style="width: 100%; min-height: 600px; overflow-y: auto; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); border-radius: 1rem; padding: 2rem;">
  <div style="text-align: center; margin-bottom: 2.5rem;">
    <div style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 0.75rem 2rem; border-radius: 9999px; box-shadow: 0 8px 16px rgba(59,130,246,0.3);">
      <div style="font-size: 1.5rem; font-weight: 800; color: white; letter-spacing: 0.025em;">{theme}</div>
    </div>
  </div>
  <div style="background: rgba(255,255,255,0.5); border-radius: 1rem; padding: 2rem; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.8);">
    {''.join(entity_html)}
  </div>
</div>'''

    def _metrics_template(self, insights: Dict[str, Any]) -> str:
        """Modern metrics dashboard template"""
        metrics = insights.get('key_metrics', {})
        sentiment = insights.get('sentiment', 'neutral')

        if not metrics:
            return '''<div style="width: 100%; min-height: 400px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); border-radius: 1rem;">
  <div style="text-align: center;">
    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; color: #475569;">No Metrics Data</div>
    <div style="font-size: 0.875rem; color: #94a3b8;">Key metrics will appear here</div>
  </div>
</div>'''

        # Modern color schemes with gradients
        colors = [
            {'primary': '#3b82f6', 'secondary': '#1e40af', 'bg': '#dbeafe'},
            {'primary': '#8b5cf6', 'secondary': '#6d28d9', 'bg': '#ede9fe'},
            {'primary': '#ec4899', 'secondary': '#be185d', 'bg': '#fce7f3'},
            {'primary': '#f59e0b', 'secondary': '#d97706', 'bg': '#fef3c7'},
            {'primary': '#10b981', 'secondary': '#059669', 'bg': '#d1fae5'},
            {'primary': '#06b6d4', 'secondary': '#0e7490', 'bg': '#cffafe'},
        ]

        metrics_html = []
        for idx, (key, value) in enumerate(list(metrics.items())[:6]):
            color = colors[idx % len(colors)]

            metrics_html.append(f'''
    <div style="position: relative; background: white; border-radius: 1rem; padding: 1.75rem; box-shadow: 0 8px 20px rgba(0,0,0,0.08); border: 2px solid {color['bg']}; overflow: hidden; transition: all 0.3s;">
      <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; background: linear-gradient(135deg, {color['primary']}22, {color['primary']}11); border-radius: 50%; opacity: 0.5;"></div>
      <div style="position: absolute; bottom: -10px; left: -10px; width: 60px; height: 60px; background: linear-gradient(135deg, {color['primary']}11, transparent); border-radius: 50%;"></div>
      <div style="position: relative; z-index: 1;">
        <div style="margin-bottom: 1rem;">
          <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">{key}</div>
        </div>
        <div style="font-size: 2.25rem; font-weight: 800; color: #0f172a; line-height: 1; margin-bottom: 0.5rem; background: linear-gradient(135deg, {color['primary']}, {color['secondary']}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
          {value}
        </div>
        <div style="height: 4px; width: 50%; background: linear-gradient(to right, {color['primary']}, transparent); border-radius: 9999px;"></div>
      </div>
    </div>''')

        # Sentiment indicator
        sentiment_config = {
            'positive': {'color': '#10b981', 'bg': '#d1fae5', 'label': 'Positive Sentiment'},
            'negative': {'color': '#ef4444', 'bg': '#fee2e2', 'label': 'Negative Sentiment'},
            'neutral': {'color': '#6b7280', 'bg': '#f3f4f6', 'label': 'Neutral Sentiment'}
        }
        sent_cfg = sentiment_config.get(sentiment.lower(), sentiment_config['neutral'])

        return f'''<div style="width: 100%; min-height: 500px; overflow-y: auto; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); border-radius: 1rem; padding: 2rem;">
  <div style="margin-bottom: 2rem; text-align: center;">
    <div style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 0.75rem 2rem; border-radius: 9999px; box-shadow: 0 8px 16px rgba(59,130,246,0.3);">
      <div style="font-size: 1.5rem; font-weight: 800; color: white; letter-spacing: 0.025em;">Key Insights Dashboard</div>
    </div>
  </div>

  <div style="background: {sent_cfg['bg']}; border: 2px solid {sent_cfg['color']}; border-radius: 1rem; padding: 1rem; margin-bottom: 2rem; text-align: center;">
    <span style="font-size: 1.125rem; font-weight: 700; color: {sent_cfg['color']};">{sent_cfg['label']}</span>
  </div>

  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
    {''.join(metrics_html)}
  </div>
</div>'''

    def _network_template(self, insights: Dict[str, Any]) -> str:
        """Network graph template"""
        entities = insights.get('entities', [])
        theme = insights.get('main_theme', 'Business Network')

        if not entities:
            return '''<div style="width: 100%; min-height: 400px; display: flex; align-items: center; justify-content: center; color: #6b7280;">
  <div style="text-align: center;">
    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">No Network Data</div>
    <div style="font-size: 0.875rem;">Entity relationships will appear here</div>
  </div>
</div>'''

        # Create a network visualization showing entity relationships
        entity_nodes = []
        colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']

        for idx, entity in enumerate(entities[:5]):
            name = entity.get('name', 'Unknown')
            entity_type = entity.get('type', 'entity')
            color = colors[idx % len(colors)]

            # Position nodes in a circular pattern
            angle = (idx / min(len(entities), 5)) * 2 * 3.14159
            x = 50 + 30 * (1 if idx == 0 else 0.8) * (0 if idx == 0 else (1 if len(entities) == 1 else ((idx - 0.5) / (len(entities) - 1) - 0.5) * 2))
            y = 50 + (0 if idx == 0 else 20 + (idx % 2) * 10)

            entity_nodes.append(f'''
      <div style="position: absolute; left: {35 + (idx * 12) % 50}%; top: {30 + (idx * 15) % 40}%; transform: translate(-50%, -50%);">
        <div style="background: {color}; color: white; padding: 0.75rem 1.25rem; border-radius: 9999px; font-weight: 600; font-size: 0.875rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); white-space: nowrap;">
          {name}
        </div>
        <div style="text-align: center; margin-top: 0.5rem; font-size: 0.75rem; color: #6b7280; font-weight: 500;">{entity_type}</div>
      </div>''')

        return f'''<div style="width: 100%; min-height: 400px; background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border-radius: 0.5rem; padding: 1.5rem; position: relative; overflow: hidden;">
  <div style="font-size: 1.25rem; font-weight: 700; color: #111827; margin-bottom: 1rem; text-align: center;">{theme}</div>
  <div style="position: relative; height: 350px;">
    {''.join(entity_nodes)}
  </div>
</div>'''

    def _trend_template(self, insights: Dict[str, Any]) -> str:
        """Trend line chart template"""
        timeline = insights.get('timeline', [])
        sentiment = insights.get('sentiment', 'neutral')

        if not timeline:
            return '''<div style="width: 100%; min-height: 400px; display: flex; align-items: center; justify-content: center; color: #6b7280;">
  <div style="text-align: center;">
    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">No Trend Data</div>
    <div style="font-size: 0.875rem;">Trend analysis will appear here</div>
  </div>
</div>'''

        # Create a visual trend representation
        sentiment_color = '#10b981' if sentiment == 'positive' else '#ef4444' if sentiment == 'negative' else '#6b7280'
        sentiment_label = sentiment.capitalize()

        trend_bars = []
        for idx, event in enumerate(timeline[:6]):
            date = event.get('date', 'N/A')
            impact = event.get('impact', 'Medium')
            event_text = event.get('event', '')[:60] + '...' if len(event.get('event', '')) > 60 else event.get('event', '')

            bar_height = 80 if impact.lower() == 'high' else 50 if impact.lower() == 'medium' else 30
            bar_color = '#ef4444' if impact.lower() == 'high' else '#f59e0b' if impact.lower() == 'medium' else '#10b981'

            trend_bars.append(f'''
      <div style="flex: 1; min-width: 80px; display: flex; flex-direction: column; align-items: center;">
        <div style="flex: 1; display: flex; align-items: flex-end; width: 100%; padding: 0 0.5rem;">
          <div style="width: 100%; height: {bar_height}%; background: linear-gradient(180deg, {bar_color}, {bar_color}aa); border-radius: 0.5rem 0.5rem 0 0; position: relative; transition: all 0.3s;">
            <div style="position: absolute; top: -1.5rem; left: 50%; transform: translateX(-50%); font-size: 0.75rem; font-weight: 600; color: {bar_color}; white-space: nowrap;">{impact}</div>
          </div>
        </div>
        <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem; text-align: center; font-weight: 500;">{date}</div>
        <div style="font-size: 0.7rem; color: #9ca3af; margin-top: 0.25rem; text-align: center; max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{event.get('event', '')}">{event_text}</div>
      </div>''')

        return f'''<div style="width: 100%; min-height: 400px; background: white; border-radius: 0.5rem; padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <div style="font-size: 1.25rem; font-weight: 700; color: #111827;">Impact Trend Over Time</div>
    <div style="background: {sentiment_color}22; color: {sentiment_color}; padding: 0.5rem 1rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; border: 2px solid {sentiment_color}44;">
      Overall: {sentiment_label}
    </div>
  </div>
  <div style="display: flex; gap: 0.5rem; height: 300px; align-items: flex-end;">
{''.join(trend_bars)}
  </div>
</div>'''

    # ========================================================================
    # Cross-Article Visualization Methods
    # ========================================================================

    def generate_cross_article_timeline(self, timeline_data: List[Dict[str, Any]]) -> str:
        """Generate cross-article timeline visualization"""
        if not timeline_data:
            return '''<div style="width: 100%; min-height: 400px; display: flex; align-items: center; justify-content: center; color: #6b7280;">
  <div style="text-align: center;">
    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">No Cross-Article Timeline Data</div>
    <div style="font-size: 0.875rem;">Timeline from multiple articles will appear here</div>
  </div>
</div>'''

        # Source colors for different articles
        source_colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4']

        timeline_html = []
        current_date = None

        for event in timeline_data[:15]:  # Show top 15 events
            date = event.get('date', 'N/A')
            event_text = event.get('event', '')
            impact = event.get('impact', 'Medium')
            source = event.get('source', 'Unknown')
            article_idx = event.get('article_index', 0)

            impact_color = '#ef4444' if impact.lower() == 'high' else '#f59e0b' if impact.lower() == 'medium' else '#10b981'
            source_color = source_colors[article_idx % len(source_colors)]

            # Add date header if new date
            if date != current_date:
                if current_date is not None:
                    timeline_html.append('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>')
                timeline_html.append(f'''
      <div style="font-size: 0.875rem; font-weight: 700; color: #3b82f6; margin-bottom: 1rem; margin-top: 1rem; text-transform: uppercase; letter-spacing: 0.05em;">
        {date}
      </div>''')
                current_date = date

            timeline_html.append(f'''
      <div style="display: flex; gap: 1rem; margin-bottom: 1rem; padding: 1rem; background: white; border-radius: 0.5rem; border-left: 4px solid {source_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="flex: 1;">
          <div style="font-weight: 600; color: #111827; margin-bottom: 0.5rem;">{event_text}</div>
          <div style="display: flex; gap: 1rem; font-size: 0.75rem;">
            <span style="background: {source_color}22; color: {source_color}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600;">{source}</span>
            <span style="background: {impact_color}22; color: {impact_color}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600;">Impact: {impact}</span>
          </div>
        </div>
      </div>''')

        return f'''<div style="width: 100%; min-height: 400px; overflow-y: auto; background: linear-gradient(135deg, #f9fafb, #f3f4f6); border-radius: 0.5rem; padding: 1.5rem;">
  <div style="font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem;">Cross-Article Timeline</div>
  <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 1.5rem;">Events from {len(set([e.get('article_index') for e in timeline_data]))} articles, sorted chronologically</div>
  <div>
    {''.join(timeline_html)}
  </div>
</div>'''

    def generate_entity_network(self, entity_data: Dict[str, Any]) -> str:
        """Generate entity network visualization"""
        entities = entity_data.get('entities', [])

        if not entities:
            return '''<div style="width: 100%; min-height: 400px; display: flex; align-items: center; justify-content: center; color: #6b7280;">
  <div style="text-align: center;">
    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">No Entity Network Data</div>
    <div style="font-size: 0.875rem;">Entity relationships will appear here</div>
  </div>
</div>'''

        # Colors for entity types
        type_colors = {
            'company': '#3b82f6',
            'person': '#10b981',
            'policy': '#f59e0b',
            'metric': '#8b5cf6',
            'organization': '#ec4899'
        }

        entity_cards = []
        for idx, entity in enumerate(entities[:10]):  # Top 10 entities
            name = entity.get('name', 'Unknown')
            entity_type = entity.get('type', 'entity')
            frequency = entity.get('frequency', 1)
            article_count = len(entity.get('article_indices', []))

            color = type_colors.get(entity_type, '#6b7280')

            # Size based on frequency
            size_class = 'large' if frequency >= 3 else 'medium' if frequency >= 2 else 'small'
            padding = '1.5rem' if size_class == 'large' else '1.25rem' if size_class == 'medium' else '1rem'
            font_size = '1.125rem' if size_class == 'large' else '1rem' if size_class == 'medium' else '0.875rem'

            entity_cards.append(f'''
      <div style="background: linear-gradient(135deg, {color}22, {color}11); border: 2px solid {color}; border-radius: 0.75rem; padding: {padding}; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: {font_size}; font-weight: 700; color: #111827; margin-bottom: 0.5rem;">{name}</div>
        <div style="font-size: 0.75rem; color: {color}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">{entity_type}</div>
        <div style="font-size: 0.75rem; color: #6b7280;">
          Mentioned in <span style="font-weight: 700; color: {color};">{article_count}</span> article{'s' if article_count > 1 else ''}
        </div>
      </div>''')

        return f'''<div style="width: 100%; min-height: 400px; background: white; border-radius: 0.5rem; padding: 1.5rem;">
  <div style="font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem;">Entity Network</div>
  <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 1.5rem;">{entity_data.get('total_unique', 0)} unique entities identified across all articles</div>
  <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;">
    {''.join(entity_cards)}
  </div>
</div>'''

    def generate_sentiment_comparison(self, sentiment_data: List[Dict[str, Any]]) -> str:
        """Generate sentiment comparison visualization"""
        if not sentiment_data:
            return '''<div style="width: 100%; min-height: 400px; display: flex; align-items: center; justify-content: center; color: #6b7280;">
  <div style="text-align: center;">
    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">No Sentiment Data</div>
    <div style="font-size: 0.875rem;">Sentiment comparison will appear here</div>
  </div>
</div>'''

        # Calculate overall sentiment
        avg_score = sum([d['sentiment_score'] for d in sentiment_data]) / len(sentiment_data)
        overall_sentiment = 'Positive' if avg_score > 0.6 else 'Negative' if avg_score < 0.4 else 'Neutral'
        overall_color = '#10b981' if avg_score > 0.6 else '#ef4444' if avg_score < 0.4 else '#6b7280'

        sentiment_bars = []
        for data in sentiment_data:
            source = data['source']
            sentiment = data['sentiment']
            score = data['sentiment_score']

            bar_width = score * 100  # 0-100%
            bar_color = '#10b981' if score > 0.6 else '#ef4444' if score < 0.4 else '#f59e0b'

            sentiment_bars.append(f'''
      <div style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
          <span style="font-size: 0.875rem; font-weight: 600; color: #111827;">{source}</span>
          <span style="font-size: 0.875rem; font-weight: 600; color: {bar_color};">{sentiment.capitalize()} ({score:.2f})</span>
        </div>
        <div style="width: 100%; height: 2rem; background: #f3f4f6; border-radius: 9999px; overflow: hidden;">
          <div style="height: 100%; width: {bar_width}%; background: linear-gradient(90deg, {bar_color}, {bar_color}cc); border-radius: 9999px; transition: width 0.5s;"></div>
        </div>
      </div>''')

        return f'''<div style="width: 100%; min-height: 400px; background: white; border-radius: 0.5rem; padding: 1.5rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <div>
      <div style="font-size: 1.5rem; font-weight: 700; color: #111827;">Sentiment Comparison</div>
      <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">How different sources covered this topic</div>
    </div>
    <div style="text-align: center; padding: 1rem; background: {overall_color}22; border: 2px solid {overall_color}; border-radius: 0.75rem;">
      <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em;">Overall</div>
      <div style="font-size: 1.5rem; font-weight: 700; color: {overall_color};">{overall_sentiment}</div>
      <div style="font-size: 0.875rem; color: #6b7280;">{avg_score:.2f}</div>
    </div>
  </div>
  <div>
    {''.join(sentiment_bars)}
  </div>
</div>'''


# ============================================================================
# Helper Functions
# ============================================================================

def create_agent() -> VisualIntelligenceAgent:
    """Factory function to create Visual Intelligence Agent"""
    return VisualIntelligenceAgent()
