import { useMutation, useQuery, UseMutationOptions } from '@tanstack/react-query';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers || {}),
      },
    });
    if (!res.ok) {
      const errorText = await res.text().catch(() => 'Unknown error');
      throw new Error(`HTTP ${res.status}: ${errorText}`);
    }
    return res.json();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Cannot connect to backend at ${API_BASE}. Make sure the backend server is running on port 8000.`);
    }
    throw error;
  }
}

export function useHealth() {
  return useQuery({ queryKey: ['health'], queryFn: () => api<{ status: string }>(`/health`) });
}

export type QueryRequest = { query: string; top_k?: number; k_final?: number };
export type Citation = { rank: number; title: string; url: string };
export type QueryResponse = {
  answer: string;
  citations: Citation[];
  confidence: number;
  telemetry: { latency_ms: number; tokens_prompt: number; tokens_completion: number; cost_usd: number };
  snippets: any[];
};

export function useQueryApi(options?: UseMutationOptions<QueryResponse, Error, QueryRequest>) {
  return useMutation<QueryResponse, Error, QueryRequest>({
    mutationKey: ['query'],
    mutationFn: (body) => api<QueryResponse>('/query', { method: 'POST', body: JSON.stringify(body) }),
    ...options,
  });
}

export function useIngest() {
  return useMutation<{ status: string }, Error, { paths: string[]; max_chunk_tokens?: number; overlap?: number }>({
    mutationKey: ['ingest'],
    mutationFn: (body) => api('/ingest', { method: 'POST', body: JSON.stringify(body) }),
  });
}

export type IngestUploadResponse = {
  status: string;
  files_processed?: number;
  filenames?: string[];
  documents_added?: number;
  chunks_added?: number;
  total_documents?: number;
  total_chunks?: number;
  recent_documents?: Array<{ id: number; title: string; source: string; created_at?: string }>;
};

export function useIngestUpload() {
  return useMutation<IngestUploadResponse, Error, { files: File[]; max_chunk_tokens?: number; overlap?: number }>({
    mutationKey: ['ingest-upload'],
    mutationFn: async ({ files, max_chunk_tokens = 512, overlap = 64 }) => {
      if (files.length === 0) {
        throw new Error('No files selected');
      }

      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });
      formData.append('max_chunk_tokens', max_chunk_tokens.toString());
      formData.append('overlap', overlap.toString());

      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
      
      try {
        const res = await fetch(`${API_BASE}/ingest/upload`, {
          method: 'POST',
          body: formData,
          // Don't set Content-Type - let browser set it with boundary for multipart/form-data
        });

        if (!res.ok) {
          const errorText = await res.text().catch(() => 'Unknown error');
          throw new Error(`HTTP ${res.status}: ${errorText}`);
        }
        return res.json();
      } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
          throw new Error(`Cannot connect to backend at ${API_BASE}/ingest/upload. Make sure the backend server is running on port 8000.`);
        }
        throw error;
      }
    },
  });
}

export function useFeedback() {
  return useMutation<{ status: string }, Error, { interaction_id: string | number; rating: number; comment?: string }>({
    mutationKey: ['feedback'],
    mutationFn: (body) => api('/feedback', { method: 'POST', body: JSON.stringify(body) }),
  });
}

export type IngestStatus = {
  status: string;
  total_documents: number;
  total_chunks: number;
  documents: Array<{
    id: number;
    title: string;
    source: string;
    url: string;
    created_at: string | null;
    chunk_count: number;
  }>;
};

export function useIngestStatus() {
  return useQuery<IngestStatus>({
    queryKey: ['ingest-status'],
    queryFn: () => api<IngestStatus>('/ingest/status'),
    refetchInterval: 5000, // Refresh every 5 seconds
  });
}


