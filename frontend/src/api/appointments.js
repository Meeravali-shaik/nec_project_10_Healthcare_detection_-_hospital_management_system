import api from "./client";

export const appointmentsApi = {
  list: () => api.get("/appointments"),
  create: (payload) => api.post("/appointments", payload),
  update: (id, payload) => api.put(`/appointments/${id}`, payload),
  changeStatus: (id, payload) => api.patch(`/appointments/${id}/status`, payload),
  remove: (id) => api.delete(`/appointments/${id}`),
};

