import api from "./client";

export const patientsApi = {
  list: (search) => api.get("/patients", { params: { search } }),
  get: (id) => api.get(`/patients/${id}`),
  create: (payload) => api.post("/patients", payload),
  update: (id, payload) => api.put(`/patients/${id}`, payload),
  remove: (id) => api.delete(`/patients/${id}`),
};

