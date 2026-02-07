import asyncio
from app.db.supabase import get_supabase_client

async def try_exec_sql():
    client = get_supabase_client()
    
    sql = "ALTER TYPE \"StrategyType\" ADD VALUE 'CUSTOM';"
    
    print(f"Attempting to run SQL via RPC 'exec_sql': {sql}")
    
    try:
        # Some setups have a helper function called exec_sql
        # This is a bit of a stretch but worth a try since the user asked
        response = client.rpc('exec_sql', {'query': sql}).execute()
        print("Success:", response)
    except Exception as e:
        print("Failed to run exec_sql RPC:", e)
        print("\nNOTE: This failure is expected if the 'exec_sql' function does not exist in your database.")
        print("You likely need to run this command in the Supabase SQL Editor manually:")
        print(f"\n{sql}\n")

if __name__ == "__main__":
    asyncio.run(try_exec_sql())
