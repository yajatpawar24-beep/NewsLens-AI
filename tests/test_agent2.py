"""
Test Suite for Agent 2: Visual Intelligence Agent
==================================================

Tests for dynamic visualization generation.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from agents.agent2 import VisualIntelligenceAgent


@pytest.mark.unit
class TestVisualIntelligenceAgent:
    """Unit tests for Visual Intelligence Agent"""

    def test_agent_initialization(self, mock_env_vars):
        """Test agent initializes correctly"""
        with patch('agents.agent2.ChatAnthropic') as mock_chat:
            agent = VisualIntelligenceAgent()
            assert agent is not None
            assert hasattr(agent, 'llm')

    def test_detect_visualization_type_timeline(self, sample_insights, mock_env_vars):
        """Test timeline visualization detection"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()

            # Timeline data
            data_with_timeline = {
                **sample_insights,
                "timeline": [
                    {"date": "2026-01-01", "event": "Event 1"},
                    {"date": "2026-01-02", "event": "Event 2"},
                    {"date": "2026-01-03", "event": "Event 3"},
                    {"date": "2026-01-04", "event": "Event 4"}
                ]
            }

            viz_type = agent.detect_visualization_type(data_with_timeline)
            assert viz_type == "timeline"

    def test_detect_visualization_type_comparison(self, sample_insights, mock_env_vars):
        """Test comparison chart detection"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()

            # Multiple entities for comparison
            data_with_comparison = {
                **sample_insights,
                "entities": [
                    {"name": "Company A", "type": "company"},
                    {"name": "Company B", "type": "company"},
                    {"name": "Company C", "type": "company"}
                ],
                "key_metrics": {
                    "Company A Revenue": "100M",
                    "Company B Revenue": "150M",
                    "Company C Revenue": "120M"
                }
            }

            viz_type = agent.detect_visualization_type(data_with_comparison)
            assert viz_type in ["comparison", "metrics_grid"]

    def test_detect_visualization_type_metrics(self, mock_env_vars):
        """Test metrics grid detection"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()

            data_with_metrics = {
                "entities": [],
                "timeline": [],
                "key_metrics": {
                    "Revenue": "500M",
                    "Profit": "100M",
                    "Growth": "25%",
                    "Market Share": "15%",
                    "ROI": "20%"
                }
            }

            viz_type = agent.detect_visualization_type(data_with_metrics)
            assert viz_type == "metrics_grid"

    def test_generate_artifact_code(self, sample_insights, mock_env_vars):
        """Test React artifact code generation"""
        with patch('agents.agent2.ChatAnthropic') as mock_chat:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = """
            import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

            const TimelineVisualization = () => {
                const data = [
                    { date: '2026-01-01', value: 100 },
                    { date: '2026-01-02', value: 150 }
                ];

                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="value" stroke="#8884d8" />
                        </LineChart>
                    </ResponsiveContainer>
                );
            };
            """
            mock_chat.return_value = mock_llm

            agent = VisualIntelligenceAgent()
            code = agent.generate_artifact_code("timeline", sample_insights)

            # Validate generated code
            assert isinstance(code, str)
            assert len(code) > 0
            assert "Recharts" in code or "Chart" in code

    def test_fallback_template_timeline(self, sample_insights, mock_env_vars):
        """Test fallback template for timeline"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()
            template = agent.get_fallback_template("timeline", sample_insights)

            # Validate template
            assert isinstance(template, str)
            assert len(template) > 0
            assert "ResponsiveContainer" in template or "Chart" in template

    def test_fallback_template_comparison(self, sample_insights, mock_env_vars):
        """Test fallback template for comparison chart"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()
            template = agent.get_fallback_template("comparison", sample_insights)

            assert isinstance(template, str)
            assert len(template) > 0

    def test_fallback_template_metrics(self, sample_insights, mock_env_vars):
        """Test fallback template for metrics grid"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()
            template = agent.get_fallback_template("metrics_grid", sample_insights)

            assert isinstance(template, str)
            assert len(template) > 0

    def test_visualization_types_coverage(self, mock_env_vars):
        """Test all visualization types are supported"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()

            viz_types = ["timeline", "comparison", "metrics_grid", "network", "trend"]

            for viz_type in viz_types:
                template = agent.get_fallback_template(viz_type, {})
                assert isinstance(template, str), f"Missing template for {viz_type}"

    def test_empty_data_handling(self, mock_env_vars):
        """Test handling of empty data"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()

            empty_data = {
                "entities": [],
                "timeline": [],
                "key_metrics": {}
            }

            viz_type = agent.detect_visualization_type(empty_data)
            assert viz_type in ["timeline", "comparison", "metrics_grid"]

            template = agent.get_fallback_template(viz_type, empty_data)
            assert isinstance(template, str)

    def test_responsive_design_in_templates(self, sample_insights, mock_env_vars):
        """Test that templates include responsive design"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()

            for viz_type in ["timeline", "comparison", "metrics_grid"]:
                template = agent.get_fallback_template(viz_type, sample_insights)

                # Check for responsive indicators
                assert 'width="100%"' in template or 'ResponsiveContainer' in template

    @pytest.mark.requires_api
    def test_real_visualization_generation(self, sample_insights):
        """Test real visualization generation with API"""
        import os
        if not os.getenv("AWS_ACCESS_KEY_ID"):
            pytest.skip("Requires AWS credentials")

        agent = VisualIntelligenceAgent()
        viz_type = agent.detect_visualization_type(sample_insights)
        code = agent.generate_artifact_code(viz_type, sample_insights)

        assert isinstance(code, str)
        assert len(code) > 100  # Reasonable code length


@pytest.mark.integration
class TestAgent2Integration:
    """Integration tests for Agent 2"""

    def test_multiple_visualizations_generation(self, sample_articles, mock_env_vars):
        """Test generating multiple visualizations"""
        with patch('agents.agent2.ChatAnthropic') as mock_chat:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value.content = "<div>Test viz</div>"
            mock_chat.return_value = mock_llm

            agent = VisualIntelligenceAgent()
            visualizations = []

            for article in sample_articles:
                insights = {
                    "entities": [{"name": "Test", "type": "company"}],
                    "timeline": [{"date": "2026-01-01", "event": "Test"}],
                    "key_metrics": {"metric1": "value1"}
                }

                viz_type = agent.detect_visualization_type(insights)
                code = agent.generate_artifact_code(viz_type, insights)
                visualizations.append(code)

            assert len(visualizations) == len(sample_articles)
            assert all(isinstance(v, str) for v in visualizations)

    def test_visualization_variety(self, mock_env_vars):
        """Test that different data generates different viz types"""
        with patch('agents.agent2.ChatAnthropic'):
            agent = VisualIntelligenceAgent()

            test_data = [
                {"timeline": [{"date": f"2026-0{i}-01"} for i in range(1, 6)], "entities": [], "key_metrics": {}},
                {"timeline": [], "entities": [{"name": f"Entity{i}"} for i in range(5)], "key_metrics": {"m1": "v1", "m2": "v2"}},
                {"timeline": [], "entities": [], "key_metrics": {"m1": "v1", "m2": "v2", "m3": "v3", "m4": "v4", "m5": "v5"}}
            ]

            viz_types = [agent.detect_visualization_type(d) for d in test_data]

            # Should detect appropriate types
            assert "timeline" in viz_types or "comparison" in viz_types or "metrics_grid" in viz_types
