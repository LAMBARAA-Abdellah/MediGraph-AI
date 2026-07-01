import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export const healthCheck = () => api.get('/health');

export const getMetrics = () => api.get('/api/metrics');

export const startSession = (patient) =>
  api.post('/sessions/start', { patient });

export const startConsultation = (threadId) =>
  api.post('/consultation/start', { thread_id: threadId });

export const submitAnswer = (threadId, answer) =>
  api.post('/consultation/answer', { thread_id: threadId, answer });

export const getConsultation = (threadId) =>
  api.get(`/consultation/${threadId}`);

export const submitPhysicianReview = (data) =>
  api.post('/consultation/physician-review', data);

export const resumeConsultation = (threadId) =>
  api.post('/consultation/resume', { thread_id: threadId });

export const getReport = (threadId) =>
  api.get(`/consultation/${threadId}/report`);

export const getPdfReport = (threadId) =>
  `${API_BASE}/consultation/${threadId}/report/pdf`;

export default api;
