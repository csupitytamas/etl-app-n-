import { defineStore } from 'pinia'

export interface ConfigData {
  schedule: string;
  custom_time?: string | null;
  condition?: string | null;
  dependency_pipeline_id?: string | null;
  uploaded_file_path?: string | null;
  uploaded_file_name?: string | null;
  field_mappings?: Record<string, any>;
  transformation?: Record<string, any>;
  selected_columns?: string[];
  group_by_columns?: string[];
  order_by_column?: string | null;
  order_direction?: string | null;
  custom_sql?: string | null;
  column_order?: string[];
  update_mode: string;
  save_option: string;
}

export const usePipelineStore = defineStore('pipeline', {
  state: () => ({
    pipeline_name: '' as string,
    source: '' as string,
    config: {} as ConfigData,
  }),
  actions: {
    reset() {
      this.pipeline_name = ''
      this.source = ''
      this.config = {
        schedule: 'daily',
        update_mode: 'append',
        save_option: 'overwrite',
      }
    }
  }
})