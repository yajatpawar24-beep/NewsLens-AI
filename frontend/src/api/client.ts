import axios from 'axios';
import type { BriefingRequest, BriefingResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds for briefing generation
});

export const generateBriefing = async (request: BriefingRequest): Promise<BriefingResponse> => {
  // Force fresh data - no caching
  console.log('🚀 Calling API with:', request);

  const response = await apiClient.post<BriefingResponse>(
    `/api/generate?_t=${Date.now()}`,
    request,
    {
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    }
  );

  console.log('✅ API Response received:', {
    summary: response.data.summary?.substring(0, 100),
    keyPoints: response.data.key_points?.length,
    visualizations: response.data.visualizations?.length,
    status: response.data.status
  });

  return response.data;
};

export const getBriefingStatus = async (id: string): Promise<BriefingResponse> => {
  const response = await apiClient.get<BriefingResponse>(`/api/status/${id}`);
  return response.data;
};

export const getAudioUrl = (id: string): string => {
  return `${API_BASE_URL}/api/audio/${id}`;
};

export const saveBriefing = async (briefing: BriefingResponse): Promise<{briefing_id: string}> => {
  const response = await apiClient.post<{briefing_id: string}>('/api/briefing/save', briefing);
  return response.data;
};

export const getBriefing = async (briefing_id: string): Promise<BriefingResponse> => {
  const response = await apiClient.get<BriefingResponse>(`/api/briefing/${briefing_id}`);
  return response.data;
};

export const exportBriefingPDF = async (briefing: BriefingResponse): Promise<Blob> => {
  const response = await apiClient.post('/api/export/pdf', briefing, {
    responseType: 'blob'
  });
  return response.data;
};

export interface RelatedArticle {
  url: string;
  title: string;
  similarity: number;
  text_preview: string;
}

export const findRelatedArticles = async (articleUrl: string, articleText?: string): Promise<RelatedArticle[]> => {
  const response = await apiClient.post<{related_articles: RelatedArticle[], count: number}>('/api/find-related', {
    article_url: articleUrl,
    article_text: articleText
  });
  return response.data.related_articles;
};

export interface QAResponse {
  answer: string;
  sources: string[];
  confidence: string;
}

export const askQuestion = async (question: string, sessionId: string): Promise<QAResponse> => {
  const response = await apiClient.post<QAResponse>('/api/qa/ask', {
    question,
    session_id: sessionId
  });
  return response.data;
};

export default apiClient;
