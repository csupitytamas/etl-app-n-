import api from './axios';

export const createPipeline = (payload) =>
  api.post('/etl/pipeline/create', payload);

export const getAllPipelines = () =>
  api.get('/etl/pipeline/all');

export const updatePipeline = (id, payload) =>
  api.put(`/etl/pipeline/update/${id}`, payload);

export const loadSchemaBySource = (source) =>
  api.post('/etl/pipeline/load-schema', { source });

export const getAvailableSources = () =>
  api.get('/etl/pipeline/available-sources');

export const loadPipelineData = (id) =>
  api.post(`/etl/pipeline/load/${id}`);