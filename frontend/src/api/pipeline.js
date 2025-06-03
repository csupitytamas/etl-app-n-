import api from './axios';

const prefix = '/etl/pipeline';

export const createPipeline = (payload) =>
  api.post(`${prefix}/create`, payload);

export const getAllPipelines = () =>
  api.get(`${prefix}/all`);

export const updatePipeline = (id, payload) =>
  api.post(`${prefix}/updated_pipeline/${id}`, payload);

export const loadSchemaBySource = (source) =>
  api.post(`${prefix}/load-schema`, { source });

export const getAvailableSources = () =>
  api.get(`${prefix}/available-sources`);

export const loadPipelineData = (id) =>
  api.post(`${prefix}/load/${id}`);
