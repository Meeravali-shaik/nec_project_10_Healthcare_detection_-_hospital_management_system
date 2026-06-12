import api from "./client";

function paramsWithPatientId(patientId) {
  return patientId ? { patient_id: patientId } : {};
}

export const aiApi = {
  summary: () => api.get("/ai/dashboard/summary"),
  predictDisease: (payload) => api.post("/ai/disease-predictions", payload),
  diseaseHistory: (patientId) => api.get("/ai/disease-predictions", { params: paramsWithPatientId(patientId) }),
  predictionHistory: (patientId) => api.get("/ai/prediction-history", { params: paramsWithPatientId(patientId) }),
  recommendTreatment: (payload) => api.post("/ai/treatment-recommendations", payload),
  treatmentHistory: (patientId) => api.get("/ai/treatment-recommendations", { params: paramsWithPatientId(patientId) }),
  predictOutcome: (payload) => api.post("/ai/outcome-predictions", payload),
  outcomeHistory: (patientId) => api.get("/ai/outcome-predictions", { params: paramsWithPatientId(patientId) }),
  analyzeReport: (payload) => api.post("/ai/report-analysis", payload),
  reportHistory: (patientId) => api.get("/ai/report-analysis", { params: paramsWithPatientId(patientId) }),
  riskAssessments: (patientId) => api.get("/ai/risk-assessments", { params: paramsWithPatientId(patientId) }),
  createRiskAssessment: (patientId) => api.post(`/ai/risk-assessments/${patientId}`),
};
