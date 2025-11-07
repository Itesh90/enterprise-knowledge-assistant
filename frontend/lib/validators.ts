import { z } from 'zod';

export const QueryRequestSchema = z.object({
  query: z.string().min(3).max(2000),
  top_k: z.number().int().min(1).max(100).optional(),
  k_final: z.number().int().min(1).max(20).optional(),
});

export const TelemetrySchema = z.object({
  latency_ms: z.number().int(),
  tokens_prompt: z.number().int(),
  tokens_completion: z.number().int(),
  cost_usd: z.number(),
});

export const CitationSchema = z.object({
  rank: z.number().int(),
  title: z.string(),
  url: z.string(),
});

export const QueryResponseSchema = z.object({
  answer: z.string(),
  citations: z.array(CitationSchema),
  confidence: z.number(),
  telemetry: TelemetrySchema,
  snippets: z.array(z.any()),
});

export type QueryRequest = z.infer<typeof QueryRequestSchema>;
export type QueryResponse = z.infer<typeof QueryResponseSchema>;


