import requests

SUPABASE_URL = "https://zrowugsybqzlnvypspqj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpyb3d1Z3N5YnF6bG52eXBzcHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk0OTkzMzAsImV4cCI6MjA2NTA3NTMzMH0.1tTmtm9HuV8Env8MwGuWD2P_9CjN4SVsBTFCT-DvZ-0"  # cseréld ki a saját kulcsodra

import os


def get_supabase_data(table_name, params=None):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Hiba történt az adatok lekérésekor: {e}")
        return []