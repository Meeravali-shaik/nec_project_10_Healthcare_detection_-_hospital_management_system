import api from "./client";

export const assistantApi = {
  sessions: () => api.get("/assistant/sessions"),
  createSession: (payload) => api.post("/assistant/sessions", payload),
  messages: (sessionId) => api.get(`/assistant/sessions/${sessionId}/messages`),
  chat: (payload) => api.post("/assistant/chat", payload),
  knowledge: () => api.get("/assistant/knowledge"),
  ingestKnowledge: (payload) => api.post("/assistant/knowledge", payload),
  searchKnowledge: (payload) => api.post("/assistant/knowledge/search", payload),
  patientCopilot: (patientId) => api.get(`/assistant/copilots/patient/${patientId}`),
  doctorCopilot: (patientId) => api.get(`/assistant/copilots/doctor/${patientId}`),
  adminCopilot: () => api.get("/assistant/copilots/admin"),
  executiveInsights: () => api.get("/assistant/insights/executive"),
  insightReports: () => api.get("/assistant/insights/reports"),
  createInsightReport: (payload) => api.post("/assistant/insights/reports", payload),
  reports: () => api.get("/assistant/reports"),
  createReport: (payload) => api.post("/assistant/reports", payload),
  memory: (sessionId) => api.get(`/assistant/memory/${sessionId}`),
  templates: () => api.get("/assistant/templates"),
  createTemplate: (payload) => api.post("/assistant/templates", payload),
};

