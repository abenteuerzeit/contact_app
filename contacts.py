import sqlite3
import json
import time
from threading import Thread
from random import random
from typing import override

# ========================================================
# Contact Model
# ========================================================
PAGE_SIZE = 100

class Contact:
    # mock contacts database
    conn: sqlite3.Connection = sqlite3.connect('contacts.db', check_same_thread=False)
    cursor: sqlite3.Cursor = conn.cursor()
    _: sqlite3.Cursor = cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first TEXT,
        last TEXT,
        phone TEXT,
        email TEXT UNIQUE
    )''')
    conn.commit()

    def __init__(self, id_: int | None = None, first: str | None = None, last: str | None = None,
                 phone: str | None = None, email: str | None = None) -> None:
        self.id: int | None = id_
        self.first: str | None = first
        self.last: str | None = last
        self.phone: str | None = phone
        self.email: str | None = email
        self.errors: dict[str, str] = {}

    @override
    def __str__(self) -> str:
        return json.dumps(obj=self.__dict__, ensure_ascii=False)

    def update(self, first: str, last: str, phone: str, email: str) -> None:
        self.first = first
        self.last = last
        self.phone = phone
        self.email = email

    def validate(self) -> bool:
        if not self.email:
            self.errors['email'] = "Email Required"
            return False

        query = 'SELECT * FROM contacts WHERE email = ? AND id != ?'
        _: sqlite3.Cursor = Contact.cursor.execute(query, (self.email, self.id if self.id else 0))
        existing_contact: sqlite3.Row | None = Contact.cursor.fetchone()
        if existing_contact:
            self.errors['email'] = "Email Must Be Unique"
            return False

        return True

    def save(self) -> bool:
        if not self.validate():
            return False

        if self.id is None:
            query = 'INSERT INTO contacts (first, last, phone, email) VALUES (?, ?, ?, ?)'
            _: sqlite3.Cursor = Contact.cursor.execute(query, (self.first, self.last, self.phone, self.email))
            self.id = Contact.cursor.lastrowid
        else:
            query = 'UPDATE contacts SET first = ?, last = ?, phone = ?, email = ? WHERE id = ?'
            _ = Contact.cursor.execute(query, (self.first, self.last, self.phone, self.email, self.id))
        Contact.conn.commit()
        return True

    def delete(self) -> None:
        if self.id is not None:
            query = 'DELETE FROM contacts WHERE id = ?'
            _: sqlite3.Cursor = Contact.cursor.execute(query, (self.id,))
            Contact.conn.commit()

    @classmethod
    def count(cls) -> int:
        time.sleep(2)
        query = 'SELECT COUNT(*) FROM contacts'
        _: sqlite3.Cursor = cls.cursor.execute(query)
        count: int = cls.cursor.fetchone()[0]
        return count

    @classmethod
    def all(cls, page: int = 1) -> list['Contact']:
        page = int(page)
        start: int = (page - 1) * PAGE_SIZE
        query = 'SELECT * FROM contacts LIMIT ? OFFSET ?'
        _: sqlite3.Cursor = cls.cursor.execute(query, (PAGE_SIZE, start))
        rows: list[sqlite3.Row] = cls.cursor.fetchall()
        return [Contact(
            id_=row[0] if isinstance(row[0], int) else None,
            first=row[1] if isinstance(row[1], str) else None,
            last=row[2] if isinstance(row[2], str) else None,
            phone=row[3] if isinstance(row[3], str) else None,
            email=row[4] if isinstance(row[4], str) else None
        ) for row in rows]

    @classmethod
    def search(cls, text: str) -> list['Contact']:
        query = 'SELECT * FROM contacts WHERE first LIKE ? OR last LIKE ? OR phone LIKE ? OR email LIKE ?'
        like_text = f'%{text}%'
        _: sqlite3.Cursor = cls.cursor.execute(query, (like_text, like_text, like_text, like_text))
        rows: list[sqlite3.Row] = cls.cursor.fetchall()
        return [Contact(
            id_=row[0] if isinstance(row[0], int) else None,
            first=row[1] if isinstance(row[1], str) else None,
            last=row[2] if isinstance(row[2], str) else None,
            phone=row[3] if isinstance(row[3], str) else None,
            email=row[4] if isinstance(row[4], str) else None
        ) for row in rows]

    @classmethod
    def find(cls, id_: int) -> 'Contact | None':
        query = 'SELECT * FROM contacts WHERE id = ?'
        _: sqlite3.Cursor = cls.cursor.execute(query, (id_,))
        row: sqlite3.Row | None = cls.cursor.fetchone()
        if row:
            return Contact(
                id_=row[0] if isinstance(row[0], int) else None,
                first=row[1] if isinstance(row[1], str) else None,
                last=row[2] if isinstance(row[2], str) else None,
                phone=row[3] if isinstance(row[3], str) else None,
                email=row[4] if isinstance(row[4], str) else None
            )
        return None


class Archiver:
    archive_status: str = "Waiting"
    archive_progress: float = 0
    thread: Thread | None = None

    def status(self) -> str:
        return Archiver.archive_status

    def progress(self) -> float:
        return Archiver.archive_progress

    def run(self) -> None:
        if Archiver.archive_status == "Waiting":
            Archiver.archive_status = "Running"
            Archiver.archive_progress = 0
            Archiver.thread = Thread(target=self.run_impl)
            Archiver.thread.start()

    def run_impl(self) -> None:
        for i in range(10):
            time.sleep(1 * random())
            if Archiver.archive_status != "Running":
                return
            Archiver.archive_progress = (i + 1) / 10
            print("Here... " + str(Archiver.archive_progress))
        time.sleep(1)
        if Archiver.archive_status != "Running":
            return
        Archiver.archive_status = "Complete"

    def archive_file(self) -> str:
        return 'contacts.db'

    def reset(self) -> None:
        Archiver.archive_status = "Waiting"

    @classmethod
    def get(cls) -> 'Archiver':
        return Archiver()
