from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from dotenv import load_dotenv, dotenv_values
import os

app = FastAPI()
load_dotenv()

class TransactionRequest(BaseModel):
    src_card: str
    dest_card: str
    amount: int


@app.post("/transaction")
def transaction(req: TransactionRequest):
    src_card = req.src_card
    dest_card = req.dest_card
    amount = req.amount
    
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT")
    )
    cur = conn.cursor()

    try:
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
        
        cur.execute("""
            WITH updated AS (
                UPDATE "Cards"
                SET balance = balance - %s
                WHERE card_number = %s AND balance >= %s
                RETURNING card_number
            )
            UPDATE "Cards"
            SET balance = balance + %s
            FROM updated
            WHERE "Cards".card_number = %s
            RETURNING "Cards".card_number;
        """, (amount, src_card, amount, amount, dest_card))
        
        result = cur.fetchone()
        
        if result is None:
                conn.rollback()
                raise HTTPException(
                    status_code=409,
                    detail="Transaction failed (insufficient balance)"
                )
        
        conn.commit()
        return {
            "message": "Transaction successful"
        }

    except HTTPException:
        # Reraise HTTPExceptions without converting to 500
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    finally:
        cur.close()
        conn.close()