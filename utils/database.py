import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client - use secrets in production, env in development
def init_supabase():
    supabase_url = st.secrets["SUPABASE_URL"] if "SUPABASE_URL" in st.secrets else os.environ.get("SUPABASE_URL")
    supabase_key = st.secrets["SUPABASE_KEY"] if "SUPABASE_KEY" in st.secrets else os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY in .env or Streamlit secrets.")
    
    return create_client(supabase_url, supabase_key)

# Initialize on import
supabase = init_supabase()

# Database operations
def store_verification(content_hash, content_uri, user_id, creation_type, creation_context=""):
    """Store content verification in database"""
    try:
        data = supabase.table("verification").insert({
            "content_hash": content_hash,
            "content_uri": content_uri,
            "user_id": user_id,
            "creation_type": creation_type,
            "creation_context": creation_context,
        }).execute()
        
        return data.data[0] if data.data else None
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None

def get_verification(content_hash):
    """Get verification status by content hash"""
    try:
        response = supabase.table("verification").select("*").eq("content_hash", content_hash).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None

def add_vouch(content_hash, voucher_id):
    """Add a vouch to content verification"""
    try:
        # First check if this user has already vouched
        # In a real implementation, you'd store vouchers separately
        
        # Get current verification
        verification = get_verification(content_hash)
        if not verification:
            return None
        
        # Update vouch count
        new_count = verification["vouches"] + 1
        status = 2 if new_count >= 3 else 1  # Update to community vouched if threshold met
        
        response = supabase.table("verification").update({
            "vouches": new_count,
            "status": status
        }).eq("content_hash", content_hash).execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None

def get_user_verifications(user_id):
    """Get all verifications by user"""
    try:
        response = supabase.table("verification").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []
