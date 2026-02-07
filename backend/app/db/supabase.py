"""
Supabase Client
Database connection and operations for PocketBuzz.
"""
from functools import lru_cache
from supabase import create_client, Client

from app.config import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get a cached Supabase client instance.
    Uses the service role key for backend operations.
    """
    settings = get_settings()
    
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise ValueError(
            "Supabase configuration missing. "
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables."
        )
    
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )


def get_public_client() -> Client:
    """
    Get a Supabase client with anon key (for frontend-facing operations).
    """
    settings = get_settings()
    
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise ValueError("Supabase configuration missing.")
    
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )
