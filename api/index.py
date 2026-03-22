from flask import Flask, redirect, request
from supabase import create_client
import os

app = Flask(__name__)

# --- FIX: Use the NAMES of the variables, not the actual URLs here ---
# These names must match what you typed into the Vercel Settings boxes
url = os.environ.get("SUPABASE_URL") 
key = os.environ.get("SUPABASE_KEY")

# Initialize client safely
if url and key:
    supabase = create_client(url, key)
else:
    supabase = None

@app.route('/')
def home():
    return "Lahe Lahe Tracker is Online. Scanning ready."

# This route catches BOTH /api/s/ID and /s/ID
@app.route('/api/s/<short_id>')
@app.route('/s/<short_id>')
def track_and_redirect(short_id):
    if not supabase:
        return "Error: Database credentials missing in Vercel settings.", 500
    
    try:
        # 1. Look up the destination
        query = supabase.table("links").select("target_url").eq("short_id", short_id).maybe_single().execute()
        
        if query.data:
            target_url = query.data['target_url']
            
            # 2. Log the analytics
            scan_data = {
                "link_id": short_id,
                "user_agent": request.headers.get('User-Agent'),
                "ip_region": request.headers.get('X-Vercel-IP-City', 'Unknown')
            }
            supabase.table("scans").insert(scan_data).execute()
            
            # 3. Redirect the user
            return redirect(target_url, code=302)
        
        return f"Error: QR ID '{short_id}' was not found in the database.", 404

    except Exception as e:
        return f"Database Connection Error: {str(e)}", 500