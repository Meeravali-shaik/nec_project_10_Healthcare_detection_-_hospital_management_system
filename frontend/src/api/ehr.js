import api from "./client";

export const ehrApi = {
  meTimeline: () => api.get("/ehr/me/timeline"),
  timeline: (patientId) => api.get(`/ehr/patients/${patientId}/timeline`),
  medicalRecords: (params) => api.get("/ehr/medical-records", { params }),
  medicalRecord: (id) => api.get(`/ehr/medical-records/${id}`),
  createMedicalRecord: (payload) => api.post("/ehr/medical-records", payload),
  updateMedicalRecord: (id, payload) => api.put(`/ehr/medical-records/${id}`, payload),
  prescriptions: (params) => api.get("/ehr/prescriptions", { params }),
  prescription: (id) => api.get(`/ehr/prescriptions/${id}`),
  createPrescription: (payload) => api.post("/ehr/prescriptions", payload),
  updatePrescription: (id, payload) => api.put(`/ehr/prescriptions/${id}`, payload),
  downloadPrescription: (id) => api.get(`/ehr/prescriptions/${id}/download`, { responseType: "blob" }),
  labReports: (params) => api.get("/ehr/lab-reports", { params }),
  createLabReport: (formData) =>
    api.post("/ehr/lab-reports", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  downloadLabReport: (id) => api.get(`/ehr/lab-reports/${id}/download`, { responseType: "blob" }),
  treatments: (params) => api.get("/ehr/treatments", { params }),
  createTreatment: (payload) => api.post("/ehr/treatments", payload),
  updateTreatment: (id, payload) => api.put(`/ehr/treatments/${id}`, payload),
  vaccinations: (params) => api.get("/ehr/vaccinations", { params }),
  createVaccination: (payload) => api.post("/ehr/vaccinations", payload),
  updateVaccination: (id, payload) => api.put(`/ehr/vaccinations/${id}`, payload),
  allergies: (params) => api.get("/ehr/allergies", { params }),
  createAllergy: (payload) => api.post("/ehr/allergies", payload),
  updateAllergy: (id, payload) => api.put(`/ehr/allergies/${id}`, payload),
};
