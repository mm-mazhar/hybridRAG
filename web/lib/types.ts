export type DocumentOut = {
  id: string;
  source_type: string;
  source_name: string;
  row_count: number;
  created_at: string | null;
};

export type PublicConfig = {
  model: string;
  models: string[];
  embedding_model: string;
};

export type ChunkOut = {
  text: string;
  filename: string | null;
  page_numbers: number[] | null;
  title: string | null;
  source: string;
};

export type RetrieveMeta = {
  hybrid: boolean;
  fts: boolean;
  multi_query: boolean;
  queries: string[];
};

export type RetrieveResponse = RetrieveMeta & {
  chunks: ChunkOut[];
};

export const EMPTY_RETRIEVE: RetrieveResponse = {
  chunks: [],
  hybrid: false,
  fts: false,
  multi_query: false,
  queries: [],
};
