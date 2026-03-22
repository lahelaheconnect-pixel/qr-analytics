from flask import Flask, redirect, request, abort
from supabase import create_client
import os

app = Flask(__name__)

# Fetch the values using the NAMES of the variables in Vercel
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Initialize the client only if the variables exist
if url and key:
    supabase = create_client(url, key)
else:
    supabase = None

@app.route('/api/s/<short_id>')
def track_and_redirect(short_id):
    try:
        if not supabase:
            return "Configuration Error: Supabase credentials not found.", 500

        # 1. Fetch the destination
        query = supabase.table("links").select("target_url").eq("short_id", short_id).maybe_single().execute()
        
        if query.data:
            target_url = query.data['target_url']
            
            # 2. Log the scan
            scan_log = {
                "link_id": short_id,
                "user_agent": request.headers.get('User-Agent'),
                "ip_region": request.headers.get('X-Vercel-IP-City', 'Unknown')
            }
            supabase.table("scans").insert(scan_log).execute()
            
            return redirect(target_url, code=302)
        else:
            return f"ID '{short_id}' not found.", 404

    except Exception as e:
        print(f"Detailed Error: {e}")
        return f"Internal Error: {str(e)}", 500