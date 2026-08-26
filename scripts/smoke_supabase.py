import os, sys
from supabase import create_client

def main() -> int:
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    sb.table("documents").select("id").limit(1).execute()
    print("supabase ok: connection + documents table reachable")
    return 0

if __name__ == "__main__":
    sys.exit(main())
