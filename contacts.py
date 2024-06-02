import json
import os
import tempfile
import time
from random import random
from threading import Thread
from typing import override

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

# Contact Model
# ========================================================

PAGE_SIZE = 100

_ = load_dotenv()

# PostgreSQL database connection
db_url = os.environ["CONTACT_APP_URL"]
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
contacts_table = Table('contacts', metadata,
                       Column('id', Integer, primary_key=True, autoincrement=True),
                       Column('first', String),
                       Column('last', String),
                       Column('phone', String),
                       Column('email', String, unique=True)
                       )

# Create the table if it doesn't exist
metadata.create_all(engine)


class Contact:
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
        query = session.query(contacts_table).filter(contacts_table.c.email == self.email,
                                                     contacts_table.c.id != self.id)
        existing_contact = query.first()
        if existing_contact:
            self.errors['email'] = "Email Must Be Unique"
            return False

        return True

    def save(self) -> bool:
        if not self.validate():
            return False

        if self.id is None:
            query = contacts_table.insert().values(first=self.first, last=self.last, phone=self.phone,
                                                   email=self.email)
            result = session.execute(query)
            self.id = result.inserted_primary_key[0]
        else:
            query = contacts_table.update().where(contacts_table.c.id == self.id).values(first=self.first,
                                                                                          last=self.last,
                                                                                          phone=self.phone,
                                                                                          email=self.email)
            session.execute(query)
        session.commit()
        return True

    def delete(self) -> None:
        if self.id is not None:
            query = contacts_table.delete().where(contacts_table.c.id == self.id)
            session.execute(query)
            session.commit()

    @classmethod
    def count(cls) -> int:
        time.sleep(2)
        query = session.query(contacts_table).count()
        return query

    @classmethod
    def all(cls, page=None):
        if page is None:
            query = session.query(contacts_table)
        else:
            page = int(page)
            start = (page) * PAGE_SIZE
            query = session.query(contacts_table).limit(PAGE_SIZE).offset(start)
        rows = query.all()
        return [Contact(
            id_=row.id,
            first=row.first,
            last=row.last,
            phone=row.phone,
            email=row.email
        ) for row in rows]

    @classmethod
    def search(cls, text):
        like_text = f'%{text}%'
        query = session.query(contacts_table).filter(
            contacts_table.c.first.like(like_text) |
            contacts_table.c.last.like(like_text) |
            contacts_table.c.phone.like(like_text) |
            contacts_table.c.email.like(like_text)
        )
        rows = query.all()
        return [Contact(
            id_=row.id,
            first=row.first,
            last=row.last,
            phone=row.phone,
            email=row.email
        ) for row in rows]

    @classmethod
    def find(cls, id_):
        query = session.query(contacts_table).filter(contacts_table.c.id == id_)
        row = query.first()
        if row:
            return Contact(
                id_=row.id,
                first=row.first,
                last=row.last,
                phone=row.phone,
                email=row.email
            )
        return None


class Archiver:
    archive_status: str = "Waiting"
    archive_progress: float = 0
    thread = None

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
            print("Here... " + str(object=Archiver.archive_progress))
        time.sleep(1)
        if Archiver.archive_status != "Running":
            return
        Archiver.archive_status = "Complete"


    def archive_file(self) -> str:
        contacts = session.query(contacts_table).all()
        csv_content = "id,first,last,phone,email\n"
        for contact in contacts:
            csv_content += f"{contact.id},{contact.first},{contact.last},{contact.phone},{contact.email}\n"

        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            temp_file.write(csv_content.encode('utf-8'))
            temp_file_path: str = temp_file.name

        return temp_file_path


    def reset(self) -> None:
        Archiver.archive_status = "Waiting"

    @classmethod
    def get(cls) -> "Archiver":
        return Archiver()

