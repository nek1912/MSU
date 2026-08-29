"""Apply schema updates to Supabase via postgrest RPC."""
import sys
sys.path.insert(0, ".")

import httpx
from app.config import get_settings

s = get_settings()
url = s.supabase_url
key = s.supabase_service_key

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

# Drop and recreate match_chunks with as_of_date parameter
sql = """
drop function if exists public.match_chunks(vector, text, text, int);

create or replace function match_chunks(
  query_embedding vector(768),
  match_domain    text,
  match_state     text,
  match_count     int default 6,
  as_of_date      date default null
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
  order by c.embedding <=> query_embedding
  limit match_count;
$$;
"""

# Try via postgrest rpc with raw SQL
r = httpx.post(
    f"{url}/rest/v1/rpc/exec_sql",
    headers=headers,
    json={"query": sql},
    timeout=30.0,
)
print(f"exec_sql: {r.status_code} {r.text[:200]}")

if r.status_code not in (200, 204):
    # Try alternative: /pg endpoint
    r2 = httpx.post(
        f"{url}/pg/query",
        headers=headers,
        json={"query": sql},
        timeout=30.0,
    )
    print(f"pg/query: {r2.status_code} {r2.text[:200]}")

# Also ensure sessions table exists
sql_sessions = """
create table if not exists sessions (
  session_id text primary key,
  state      jsonb default '{}',
  expires_at timestamptz,
  created_at timestamptz default now()
);

create or replace function purge_expired_sessions()
returns void
language sql
as $$
  delete from sessions where expires_at < now();
$$;
"""

r3 = httpx.post(
    f"{url}/rest/v1/rpc/exec_sql",
    headers=headers,
    json={"query": sql_sessions},
    timeout=30.0,
)
print(f"sessions: {r3.status_code} {r3.text[:200]}")
