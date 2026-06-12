import api from "./client";

export const doctorsApi = {
  list: (search) => api.get("/doctors", { params: { search } }),
  get: (id) => api.get(`/doctors/${id}`),
  create: (payload) => api.post("/doctors", payload),
  update: (id, payload) => api.put(`/doctors/${id}`, payload),
  remove: (id) => api.delete(`/doctors/${id}`),
};

