import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  current_stage: string;
  current_version: number;
  revision_count: number;
  max_iterations: number;
  max_revisions: number;
  experiment_type: string;
  approval_status: string;
  created_at?: string;
  updated_at?: string;
}

export const api = {
  getProjects: async () => {
    const response = await axios.get(`${API_URL}/projects/`);
    return response.data;
  },
  createProject: async (data: { name: string; description: string; max_iterations: number; experiment_type: string }) => {
    const response = await axios.post(`${API_URL}/projects/`, data);
    return response.data;
  },
  getProject: async (projectId: string) => {
    const response = await axios.get(`${API_URL}/projects/${projectId}`);
    return response.data;
  },
  getProjectStatus: async (projectId: string) => {
    const response = await axios.get(`${API_URL}/projects/${projectId}/status`);
    return response.data;
  },
  startProject: async (projectId: string) => {
    const response = await axios.post(`${API_URL}/projects/${projectId}/start`);
    return response.data;
  },
  retryProject: async (projectId: string) => {
    const response = await axios.post(`${API_URL}/projects/${projectId}/retry`);
    return response.data;
  },
  approveProject: async (projectId: string) => {
    const response = await axios.post(`${API_URL}/projects/${projectId}/approve`);
    return response.data;
  },
  reviseProject: async (projectId: string, feedback: string) => {
    const response = await axios.post(`${API_URL}/projects/${projectId}/revise`, { feedback });
    return response.data;
  },
  deleteProject: async (projectId: string) => {
    const response = await axios.delete(`${API_URL}/projects/${projectId}`);
    return response.data;
  },
  getRequirements: async (projectId: string) => {
    const response = await axios.get(`${API_URL}/projects/${projectId}/requirements`);
    return response.data;
  },
  getPlan: async (projectId: string) => {
    const response = await axios.get(`${API_URL}/projects/${projectId}/plan`);
    return response.data;
  },
  getFiles: async (projectId: string, version?: number) => {
    const url = version
      ? `${API_URL}/projects/${projectId}/files?version=${version}`
      : `${API_URL}/projects/${projectId}/files`;
    const response = await axios.get(url);
    return response.data;
  },
  getFileContent: async (projectId: string, path: string, version?: number) => {
    const encodedPath = path.split('/').map(encodeURIComponent).join('/');
    const url = version
      ? `${API_URL}/projects/${projectId}/files/${encodedPath}?version=${version}`
      : `${API_URL}/projects/${projectId}/files/${encodedPath}`;
    const response = await axios.get(url, { responseType: 'text' });
    return response.data;
  },
  getIterations: async (projectId: string) => {
    const response = await axios.get(`${API_URL}/projects/${projectId}/iterations`);
    return response.data;
  },
  getTestResults: async (projectId: string, version?: number) => {
    const url = version
      ? `${API_URL}/projects/${projectId}/tests?version=${version}`
      : `${API_URL}/projects/${projectId}/tests`;
    const response = await axios.get(url);
    return response.data;
  },
  getReviewResults: async (projectId: string, version?: number) => {
    const url = version
      ? `${API_URL}/projects/${projectId}/review?version=${version}`
      : `${API_URL}/projects/${projectId}/review`;
    const response = await axios.get(url);
    return response.data;
  },
  getDebugResults: async (projectId: string, version?: number) => {
    const url = version
      ? `${API_URL}/projects/${projectId}/debug?version=${version}`
      : `${API_URL}/projects/${projectId}/debug`;
    const response = await axios.get(url);
    return response.data;
  },
  getEvaluation: async (projectId: string, version?: number) => {
    const url = version
      ? `${API_URL}/projects/${projectId}/evaluation?version=${version}`
      : `${API_URL}/projects/${projectId}/evaluation`;
    const response = await axios.get(url);
    return response.data;
  },
  getDocumentation: async (projectId: string) => {
    const response = await axios.get(`${API_URL}/projects/${projectId}/documentation`);
    return response.data;
  },
  getVersions: async (projectId: string) => {
    const response = await axios.get(`${API_URL}/projects/${projectId}/versions`);
    return response.data;
  },
  getVersionDetail: async (projectId: string, version: number) => {
    const response = await axios.get(`${API_URL}/projects/${projectId}/versions/${version}`);
    return response.data;
  },
  getPackage: async (projectId: string) => {
    try {
      const response = await axios.get(`${API_URL}/projects/${projectId}/package`);
      return response.data;
    } catch {
      return null;
    }
  },
  getDownloadUrl: (projectId: string) => {
    return `${API_URL}/projects/${projectId}/download`;
  },
  getPreviewUrl: (projectId: string, version?: number) => {
    const baseUrl = API_URL.replace('/api', '');
    const v = version || 1;
    return `${baseUrl}/projects/${projectId}/versions/v${v}/index.html`;
  },
  getProjectAgents: async (projectId: string) => {
    try {
      const response = await axios.get(`${API_URL}/projects/${projectId}/agents`);
      return response.data;
    } catch {
      return [];
    }
  },
};
