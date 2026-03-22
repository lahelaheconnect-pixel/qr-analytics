from flask import Flask, request, redirect
from supabase import create_client
import os

app = Flask(__name__)

# Fetch credentials from Vercel Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/s/<short_id>')
def track_and_redirect(short_id):
    # 1. Look up the target URL in Supabase
    result = supabase.table("links").select("target_url").eq("short_id", short_id).single().execute()
    
    if result.data:
        target_url = result.data['target_url']
        
        # 2. Log the scan analytics
        scan_data = {
            "link_id": short_id,
            "user_agent": request.headers.get('User-Agent'),
            "ip_region": request.headers.get('X-Vercel-IP-City', 'Unknown')
        }
        supabase.table("scans").insert(scan_data).execute()
        
        # 3. Redirect the user
        return redirect(target_url, code=302)
    
    return "Link not found", 404
