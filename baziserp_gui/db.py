import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        dbname="baziserp",
        user="postgres",
        password="4Bignaggi7",
        host="db.zrowugsybqzlnvypspqj.supabase.co",
        port=5432
    )
