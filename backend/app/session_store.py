from datetime import datetime, timedelta, timezone

from app.db import get_supabase


def get_state(session_id: str) -> str | None:
    """Session is authoritative for jurisdiction (spec §2.3, P1-7): a request
    with state=null continues in the session's previously selected state."""
    rows = (get_supabase().table("sessions").select("state")
            .eq("session_id", session_id).limit(1).execute().data or [])
    if not rows:
        return None
    return (rows[0].get("state") or {}).get("selected_state")


def touch_session(session_id: str, selected_state: str | None, language: str) -> None:
    sb = get_supabase()
    try:
        sb.rpc("purge_expired_sessions", {}).execute()
    except Exception:
        pass  # RPC may not exist until migration 0002 is applied
    expires = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    sb.table("sessions").upsert({
        "session_id": session_id,
        "state": {"selected_state": selected_state, "language": language},
        "expires_at": expires,
    }, on_conflict="session_id").execute()
