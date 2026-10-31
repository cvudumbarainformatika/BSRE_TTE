import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8005/api/v1",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("Sesi kadaluarsa. Silakan login kembali.");
    }
    return Promise.reject(error);
  }
);

export const documentApi = {
  upload: (kunjunganId: number | string, formData: FormData) =>
    api.post(`/document/${kunjunganId}/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),

  generateSimrs: (payload: any) =>
    api.post("/document/generate-simrs", payload),

  finalizeSuratKematianRanap: (payload: any) =>
    api.post("/simrs/ranap/surat-kematian/finalize", payload),

  getMysqlSuratKematianList: (params?: { limit?: number; search?: string; auto_sync?: boolean }) =>
    api.get("/simrs/ranap/surat-kematian/mysql-list", { params }),

  syncMysqlSuratKematian: (limit = 20) =>
    api.post("/simrs/ranap/surat-kematian/sync-mysql", null, { params: { limit } }),

  getSuratKematianRanapStatus: (noreg: string) =>
    api.get("/simrs/ranap/surat-kematian/status", { params: { noreg } }),

  list: (params: any) => api.get("/document", { params }),

  getById: (id: number | string) => api.get(`/document/${id}`),

  getViewUrl: (id: number | string) =>
    `${api.defaults.baseURL}/document/${id}/view`,

  getDownloadUrl: (id: number | string) =>
    `${api.defaults.baseURL}/document/${id}/download`,

  approve: (id: number | string, payload: { approved: boolean; catatan?: string }) =>
    api.post(`/document/${id}/approve`, payload),

  semanticSearch: (query: string, limit = 10) =>
    api.post("/document/semantic-search", { query, limit }),

  delete: (id: number | string) => api.delete(`/document/${id}`),

  // TTE BSRE Tunggal & Batch Sign
  signTte: (id: number | string, payload: { passphrase?: string; catatan?: string } = {}) =>
    api.post(`/tte/${id}/sign`, payload),

  batchSignTte: (payload: { document_ids: number[]; passphrase?: string; catatan?: string }) =>
    api.post("/tte/batch-sign", payload),

  getPendingMyDocuments: (params?: { document_type?: string }) =>
    api.get("/tte/pending-my-documents", { params }),

  verifyTte: (id: number | string) => api.get(`/tte/${id}/verify`),

  // Audit Trail
  getAuditTrail: (id: number | string) => api.get(`/audit/document/${id}`),
};

export const notificationApi = {
  getMyNotifications: () => api.get("/notifications/my"),
  getUnreadCount: () => api.get("/notifications/unread-count"),
  markRead: (id: number | string) => api.post(`/notifications/${id}/read`),
};

export const uploadTteApi = {
  convertAndPreview: (formData: FormData) =>
    api.post("/upload-tte/convert-preview", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),

  getPagePreviewUrl: (uploadId: string, pageNumber: number) =>
    `${api.defaults.baseURL}/upload-tte/page-preview/${uploadId}/${pageNumber}`,

  processSign: (formData: FormData) =>
    api.post("/upload-tte/process-sign", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

export const authApi = {
  login: (credentials: { username: string; password: string }) =>
    api.post("/auth/login", credentials),
  loginQrSimrs: (payload: { email: string; token?: string }) =>
    api.post("/auth/login-qr", payload),
  ssoLogin: (payload: { sso_token?: string; nip?: string; username?: string; auth_key?: string }) =>
    api.post("/auth/sso-login", payload),
  generateQr: (customCode?: string) =>
    api.post("/auth/qr/generate", customCode ? { custom_code: customCode } : {}),
  checkQrStatus: (sessionId: string) => api.get(`/auth/qr/status/${sessionId}`),
  approveQr: (payload: { session_id: string; nip: string }) => api.post("/auth/qr/approve", payload),
  me: () => api.get("/auth/me"),
};

export default api;
