const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export type DocumentRecord = {
  id: string;
  filename: string;
  title: string;
  field: string;
  status: string;
  char_count: number;
  created_at: string;
};

export async function uploadDocument(file: File, field: string) {
  const form = new FormData();
  form.set('file', file);
  form.set('field', field);
  return request<{ document: DocumentRecord }>('/v1/documents/upload', {
    method: 'POST',
    body: form
  });
}

export async function listDocuments() {
  return request<{ documents: DocumentRecord[] }>('/v1/documents');
}

export async function analyzeDocument(document_id: string, query: string) {
  return request<any>('/v1/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id, query, mode: 'full' })
  });
}

export async function queryDocument(document_id: string, query: string) {
  return request<any>('/v1/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id, query, top_k: 8 })
  });
}

export async function getChemistryDatasets() {
  return request<any>('/v1/chemistry/datasets');
}
