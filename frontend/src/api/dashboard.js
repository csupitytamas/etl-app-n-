import api from './axios';
export const getDashboardPipelines = () => api.get('/etl/dashboard');