-- Task 3: Schema Migration — entity_id on documents
-- Adds optional entity_id column to documents table for per-scheme/per-entity filtering.

-- 1. Add entity_id column to documents
alter table documents add column if not exists entity_id text;

-- 2. Partial index for efficient entity filtering (only non-null rows)
create index if not exists idx_documents_entity_id on documents(entity_id) where entity_id is not null;

-- 3. Update match_chunks RPC to accept match_entity_id parameter
create or replace function match_chunks(
  query_embedding vector(768),
  match_domain    text,
  match_state     text,
  match_count     int default 6,
  as_of_date      date default null,
  match_entity_id text default null
)
returns table (
  chunk_id       uuid,
  stable_chunk_id text,
  document_id    uuid,
  title          text,
  page           int,
  page_start     int,
  page_end       int,
  section        text,
  subsection     text,
  clause         text,
  content        text,
  similarity     float,
  source_url     text,
  source_file    text,
  domain         text,
  jurisdiction   text,
  state          text
)
language sql stable
set hnsw.ef_search = 40
as $$
  select c.id,
         coalesce(c.stable_chunk_id, c.id::text),
         c.document_id,
         d.title,
         c.page,
         coalesce(c.page_start, c.page),
         coalesce(c.page_end, c.page),
         coalesce(c.section, ''),
         c.subsection,
         c.clause,
         c.content,
         1 - (c.embedding <=> query_embedding) as similarity,
         coalesce(c.source_url, d.source_url, '') as source_url,
         c.source_file,
         coalesce(c.domain, d.domain, match_domain),
         coalesce(c.jurisdiction, d.jurisdiction, 'central'),
         c.state
  from chunks c
  join documents d on d.id = c.document_id
  where c.domain = match_domain
    and (match_state is null or c.state is null or c.state = match_state)
    and (as_of_date is null or d.effective_date is null or d.effective_date <= as_of_date)
    and (match_entity_id is null or d.entity_id = match_entity_id)
  order by c.embedding <=> query_embedding
  limit match_count;
$$;

-- 4. Update match_chunks_lexical RPC to accept match_entity_id parameter
create or replace function match_chunks_lexical(
  query_text text,
  match_domain text default null,
  match_state text default null,
  match_count int default 6,
  match_entity_id text default null
)
returns table (
  chunk_id uuid,
  stable_chunk_id text,
  document_id uuid,
  title text,
  organization text,
  jurisdiction text,
  state text,
  domain text,
  source_url text,
  source_file text,
  page int,
  page_start int,
  page_end int,
  section text,
  subsection text,
  clause text,
  content text,
  similarity float
)
language sql stable as $$
  select c.id,
         c.stable_chunk_id,
         d.id,
         d.title,
         d.organization,
         d.jurisdiction,
         d.state,
         d.domain,
         d.source_url,
         d.source_file,
         c.page,
         c.page,
         c.page,
         c.section,
         c.metadata->>'subsection',
         c.metadata->>'clause',
         c.content,
         -- Lexical similarity: ts_rank_cd with normalization
         ts_rank_cd(c.content_fts, plainto_tsquery('english', unaccent(query_text))) as similarity
  from chunks c
  join documents d on d.id = c.document_id
  where c.content_fts @@ plainto_tsquery('english', unaccent(query_text))
    and (match_domain is null or d.domain = match_domain)
    and (
      d.jurisdiction = 'central'
      or (match_state is not null and d.state = match_state)
    )
    and (match_entity_id is null or d.entity_id = match_entity_id)
  order by ts_rank_cd(c.content_fts, plainto_tsquery('english', unaccent(query_text))) desc
  limit least(match_count, 20);
$$;
