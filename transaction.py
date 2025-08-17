from fastapi import FastAPI, HTTPException
import psycopg2
from dotenv import load_dotenv, dotenv_values
import os

app = FastAPI()



@app.post("/transaction")
def transaction(src_card: str, dest_card: str, amount: int):
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT")
    )
    cur = conn.cursor()

    cur.execute('SELECT card_number FROM "Cards" WHERE card_number = %s', (src_card,))
    if cur.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail="Source card not found"
        )
    
    cur.execute('SELECT card_number FROM "Cards" WHERE card_number = %s', (dest_card,))
    if cur.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail="Destination card not found"
        )
    
    conn.commit()

    cur.close()
    conn.close()