import { EventEmitter } from './events';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5173';
const BASE_URL = API_URL;

export enum WidgetType {
  TABLE = 'TABLE',
  LINE_CHART = 'LINE_CHART',
  BAR_CHART = 'BAR_CHART',
  PIE_CHART = 'PIE_CHART',
  NUMBER = 'NUMBER',
  TEXT = 'TEXT'
}

export interface SQLTemplate {
  id: number;
  name: string;
  description?: string;
  query: string;
  source_question: string;
  widget_type: WidgetType;
  refresh_rate: number;
  created_at: string;
  updated_at?: string;
  last_execution?: string;
}

export interface TemplateCreate {
  name: string;
  description?: string;
  query: string;
  source_question: string;
  widget_type: WidgetType;
  refresh_rate: number;
}

class TemplateService {
  private static instance: TemplateService;
  private templates: Map<number, SQLTemplate> = new Map();
  private eventEmitter = new EventEmitter();
  private isLoading = false;

  private constructor() {
    // Private constructor for singleton pattern
  }

  public static getInstance(): TemplateService {
    if (!TemplateService.instance) {
      TemplateService.instance = new TemplateService();
    }
    return TemplateService.instance;
  }

  public getAllTemplates(): SQLTemplate[] {
    return Array.from(this.templates.values());
  }

  public getTemplate(id: number): SQLTemplate | undefined {
    return this.templates.get(id);
  }

  public async fetchTemplates(): Promise<void> {
    if (this.isLoading) return;
    
    try {
      this.isLoading = true;
      const response = await fetch(`${BASE_URL}/api/templates/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const templates: SQLTemplate[] = await response.json();
      
      // Update cache
      this.templates.clear();
      templates.forEach(template => {
        this.templates.set(template.id, template);
      });
      
      this.eventEmitter.emit('templates_updated', Array.from(this.templates.values()));
    } catch (error) {
      console.error('Error fetching templates:', error);
      this.eventEmitter.emit('error', error);
    } finally {
      this.isLoading = false;
    }
  }

  public async createTemplate(template: TemplateCreate): Promise<SQLTemplate> {
    try {
      const response = await fetch(`${BASE_URL}/api/templates/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(template),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const newTemplate: SQLTemplate = await response.json();
      this.templates.set(newTemplate.id, newTemplate);
      this.eventEmitter.emit('template_created', newTemplate);
      return newTemplate;
    } catch (error) {
      console.error('Error creating template:', error);
      this.eventEmitter.emit('error', error);
      throw error;
    }
  }

  public async updateTemplate(id: number, template: Partial<TemplateCreate>): Promise<SQLTemplate> {
    try {
      const response = await fetch(`${BASE_URL}/api/templates/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(template),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const updatedTemplate: SQLTemplate = await response.json();
      this.templates.set(updatedTemplate.id, updatedTemplate);
      this.eventEmitter.emit('template_updated', updatedTemplate);
      return updatedTemplate;
    } catch (error) {
      console.error('Error updating template:', error);
      this.eventEmitter.emit('error', error);
      throw error;
    }
  }

  public async deleteTemplate(id: number): Promise<void> {
    try {
      const response = await fetch(`${BASE_URL}/api/templates/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      this.templates.delete(id);
      this.eventEmitter.emit('template_deleted', id);
    } catch (error) {
      console.error('Error deleting template:', error);
      this.eventEmitter.emit('error', error);
      throw error;
    }
  }

  public onTemplatesUpdated(callback: (templates: SQLTemplate[]) => void): void {
    this.eventEmitter.on('templates_updated', callback);
  }

  public onTemplateCreated(callback: (template: SQLTemplate) => void): void {
    this.eventEmitter.on('template_created', callback);
  }

  public onTemplateUpdated(callback: (template: SQLTemplate) => void): void {
    this.eventEmitter.on('template_updated', callback);
  }

  public onTemplateDeleted(callback: (id: number) => void): void {
    this.eventEmitter.on('template_deleted', callback);
  }

  public onError(callback: (error: any) => void): void {
    this.eventEmitter.on('error', callback);
  }

  public offTemplatesUpdated(callback: (templates: SQLTemplate[]) => void): void {
    this.eventEmitter.off('templates_updated', callback);
  }

  public offTemplateCreated(callback: (template: SQLTemplate) => void): void {
    this.eventEmitter.off('template_created', callback);
  }

  public offTemplateUpdated(callback: (template: SQLTemplate) => void): void {
    this.eventEmitter.off('template_updated', callback);
  }

  public offTemplateDeleted(callback: (id: number) => void): void {
    this.eventEmitter.off('template_deleted', callback);
  }

  public offError(callback: (error: any) => void): void {
    this.eventEmitter.off('error', callback);
  }
}

export const templateService = TemplateService.getInstance(); 