from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv, dotenv_values
import os
from contextlib import contextmanager

app = FastAPI()
load_dotenv()

db_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)

@contextmanager
def get_db_connection():
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)

@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


class TransactionRequest(BaseModel):
    src_card: str
    dest_card: str
    amount: int


@app.post("/transaction")
async def transaction(req: TransactionRequest):
    src_card = req.src_card
    dest_card = req.dest_card
    amount = req.amount

    try:
        with get_db_cursor(commit=True) as cur:

            # Lock the source card row for update to ensure concurrency safety
            cur.execute("""SELECT card_number, balance
                FROM "Cards"
                WHERE card_number IN (%s, %s)
                FOR UPDATE;
            """, (src_card, dest_card))
            rows = cur.fetchall()
            if len(rows) != 2:
                raise HTTPException(
                    status_code=404,
                    detail="card not found"
                )
            # Map balances to src and dest
            balances = {row[0]: row[1] for row in rows}
            src_balance = balances[src_card]
            dest_balance = balances[dest_card]

            if src_balance < amount:
                raise HTTPException(
                    status_code=200,
                    detail="Transaction failed (insufficient balance)"
                )
            
            # Debit source card
            cur.execute('UPDATE "Cards" SET balance = balance - %s WHERE card_number = %s', (amount, src_card))
            # Credit destination card
            cur.execute('UPDATE "Cards" SET balance = balance + %s WHERE card_number = %s', (amount, dest_card))

            cur.execute("""
                INSERT INTO logs(src_card_number, dest_card_number, amount)
                VALUES(%s, %s, %s)
            """, (src_card, dest_card, amount))

    except HTTPException:
        # Reraise HTTPExceptions without converting to 500
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    return {"message": "Transaction successful"}

@app.get("/get-balance")
async def get_balance(card_number: str):
    try:
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                SELECT balance from "Card"
                WHERE card_number = %s
            """, (card_number,))

            balance = cur.fetchone()
            if balance is None:
                raise HTTPException(
                    status_code=404,
                    detail="Card number not found"
                )
            return {"balance": balance}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )