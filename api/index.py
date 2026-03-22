from flask import Flask, redirect, request, abort
from supabase import create_client
import os

app = Flask(__name__)

# Use the exact names you set in Vercel Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/s/<short_id>')
def track_and_redirect(short_id):
    try:
        # 1. Fetch the destination from Supabase
        # We use .maybe_single() to avoid errors if the ID doesn't exist
        query = supabase.table("links").select("target_url").eq("short_id", short_id).maybe_single().execute()
        
        if query.data:
            target_url = query.data['target_url']
            
            # 2. Log the scan to your 'scans' table
            # We gather basic marketing data from the request headers
            scan_log = {
                "link_id": short_id,
                "user_agent": request.headers.get('User-Agent'),
                "ip_region": request.headers.get('X-Vercel-IP-City', 'Unknown')
            }
            supabase.table("scans").insert(scan_log).execute()
            
            # 3. Perform the redirect
            return redirect(target_url, code=302)
        
        else:
            return f"Error: The ID '{short_id}' was not found in the database.", 404

    except Exception as e:
        print(f"Server Error: {e}")
        return "Internal Server Error", 500