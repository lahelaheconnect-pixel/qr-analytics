from flask import Flask, redirect, request, abort
from supabase import create_client
import os

app = Flask(__name__)

# CORRECT WAY: 
# os.environ.get looks for the NAME of the variable in Vercel Settings, 
# not the actual value itself.
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize the client
# If the variables above are correctly set in Vercel, this will now succeed.
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/s/<short_id>')
def track_and_redirect(short_id):
    try:
        # 1. Fetch the destination from Supabase
        query = supabase.table("links").select("target_url").eq("short_id", short_id).maybe_single().execute()
        
        if query.data:
            target_url = query.data['target_url']
            
            # 2. Log the scan to your 'scans' table
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