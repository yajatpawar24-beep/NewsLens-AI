"""
NewsLens AI Agent System
========================

This package contains the 3-agent architecture for multi-modal news intelligence:

- Agent 1 (Source Intelligence): Extracts structured insights from articles
- Agent 2 (Visual Intelligence): Generates dynamic visualizations
- Agent 3 (Briefing Synthesis): Creates comprehensive briefings with audio

All agents are orchestrated via LangGraph StateGraph in orchestrator.py
"""

from .agent1 import SourceIntelligenceAgent
from .agent2 import VisualIntelligenceAgent
from .agent3 import BriefingSynthesisAgent

__all__ = [
    'SourceIntelligenceAgent',
    'VisualIntelligenceAgent',
    'BriefingSynthesisAgent'
]
