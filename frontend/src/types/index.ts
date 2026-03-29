export interface Entity {
  name: string;
  type: 'company' | 'person' | 'policy' | 'metric';
  context: string;
}

export interface TimelineEvent {
  date: string;
  event: string;
  impact: string;
}

export interface Relationship {
  source: string;
  target: string;
  type: string;
  strength: number;
}

export interface EntityGraph {
  entities: Entity[];
  relationships: Relationship[];
}

export interface ArticleInsights {
  entities: Entity[];
  timeline: TimelineEvent[];
  key_metrics: Record<string, string>;
  sentiment: 'positive' | 'negative' | 'neutral';
  main_theme: string;
}

export interface Briefing {
  summary: string;
  key_points: string[];
  insights: {
    contradictions?: string[];
    consensus?: string[];
  };
  questions: string[];
  visualizations: string[];
  audio_url: string;  // Changed from audio_path to audio_url
  entity_graph: EntityGraph;
  session_id: string;  // Session ID for Q&A
  status: string;
}

export interface QARequest {
  question: string;
  session_id: string;
}

export interface QAResponse {
  answer: string;
  sources: string[];
  confidence: string;
}

export interface BriefingRequest {
  article_urls: string[];
}

export interface BriefingResponse extends Briefing {}
