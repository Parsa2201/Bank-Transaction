import psycopg2
import os
from tqdm import tqdm
import io
from contextlib import contextmanager

# TOTAL_CARDS = 100_000_000
TOTAL_CARDS = 1_000_000
CHUNK_SIZE = 1_000_000
DEFAULT_BALANCE = 1000

class SingleDatabaseConnection:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            host=os.getenv("DATABASE_HOST"),
            port=os.getenv("DATABASE_PORT")
        )
        self.cur = self.conn.cursor()
    
    @contextmanager
    def get_cursor(self):
        try:
            yield self.cur
        except:
            self.conn.rollback()
        finally:
            self.conn.commit()
    
    def close(self):
        self.cur.close()
        self.conn.close()


class CardLoader:
    def __init__(self, total_cards=TOTAL_CARDS, chunk_size=CHUNK_SIZE, default_balance=DEFAULT_BALANCE):
        self.total_cards = total_cards
        self.total_primary_cards = 0
        self.chunk_size = chunk_size
        self.default_balance = default_balance

    def connect_to_database(self, db_conn: SingleDatabaseConnection):
        self.db_conn = db_conn

    def load_cards(self):
        self._clear_database()
        self._drop_index()
        self._load_primary_cards()
        self._load_range_of_cards()
        self._create_index()

    def _clear_database(self):
        with self.db_conn.get_cursor() as cur:
            cur.execute('TRUNCATE TABLE cards RESTART IDENTITY CASCADE')
            cur.execute('TRUNCATE TABLE logs RESTART IDENTITY CASCADE')


    def _drop_index(self):
        with self.db_conn.get_cursor() as cur:
            cur.execute('DROP INDEX IF EXISTS idx_cards_card_number;')

    def _create_index(self):
        with self.db_conn.get_cursor() as cur:
            cur.execute('CREATE INDEX idx_cards_card_number ON cards(card_number);')

    def _load_primary_card(self, card_number, balance):
        with self.db_conn.get_cursor() as cur:
            cur.execute(
                'INSERT INTO cards (card_number, balance) VALUES (%s, %s)',
                (card_number, balance)
            )
            self.total_primary_cards += 1

    def _load_primary_cards(self):
        self._load_primary_card("0000000000000000", 1000)
        self._load_primary_card("1111111111111111", 1000)


    def _load_range_of_cards(self):
        for start_card_number in tqdm(range(2, self.total_cards + 2, self.chunk_size), 
                                      desc="Loading cards", 
                                      unit="chunk"):
            self._load_chunk_of_cards(start_card_number)

    def _load_chunk_of_cards(self, start_card_number):
        buffer = io.StringIO()
        for i in self._get_chunk_card_number_range(start_card_number):
            self._write_card_into_buffer(f"{i:016d}", buffer)
        self._load_buffer_to_database(buffer)

    def _get_chunk_card_number_range(self, start_card_number):
        end_card_number = min(start_card_number + self.chunk_size, self.total_cards + self.total_primary_cards)
        return range(start_card_number, end_card_number)

    def _write_card_into_buffer(self, card_number, buffer: io.StringIO):
        balance = self.default_balance
        buffer.write(f"{card_number}\t{balance}\n")

    def _load_buffer_to_database(self, buffer: io.StringIO):
        with self.db_conn.get_cursor() as cur:
            buffer.seek(0)
            cur.copy_from(buffer, 'cards', columns=('card_number', 'balance'), sep='\t')


def load_database():
    db_conn = SingleDatabaseConnection()
    loader = CardLoader()
    loader.connect_to_database(db_conn)
    loader.load_cards()
    db_conn.close()


if __name__ == "__main__":
    load_database()