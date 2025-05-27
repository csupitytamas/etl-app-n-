import api from './axios';

export const createPipeline = (payload) =>
  api.post('/etl/pipeline/create', payload);

export const getAllPipelines = () =>
  api.get('/etl/pipeline/all');

export const updatePipeline = (id, payload) =>
  api.put(`/etl/pipeline/update/${id}`, payload);