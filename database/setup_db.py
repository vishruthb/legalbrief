from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    # Initialize Supabase client
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    
    # Create briefs table
    briefs_table = """
    create table if not exists briefs (
        brief_id uuid default uuid_generate_v4() primary key,
        document_type text not null,
        parsed_content jsonb,
        upload_timestamp timestamp with time zone default timezone('utc'::text, now()),
        is_demo boolean default false
    );
    """
    
    # Create links table
    links_table = """
    create table if not exists links (
        link_id uuid default uuid_generate_v4() primary key,
        brief_pair_id uuid references briefs(brief_id),
        moving_brief_heading text,
        response_brief_heading text,
        similarity_score float,
        explanation text,
        created_at timestamp with time zone default timezone('utc'::text, now())
    );
    """
    
    try:
        # Execute table creation
        supabase.table("briefs").select("*").limit(1).execute()
        print("✅ Connected to Supabase successfully")
        
        # Create tables using raw SQL
        supabase.query(briefs_table).execute()
        print("✅ Created briefs table")
        
        supabase.query(links_table).execute()
        print("✅ Created links table")
        
        print("\nDatabase setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")

if __name__ == "__main__":
    setup_database()
