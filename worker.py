#!/usr/bin/env python3
from os import environ
from time import time
from time import sleep
from datetime import datetime
from datetime import timedelta
from logging import INFO
from logging import getLogger
from logging import Formatter
from logging import StreamHandler

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.models import Vote
from app.models import Session
from app.models import Option

engine = None


def init_engine():
    load_dotenv()
    globals().update({
        "engine": create_engine(environ.get("SQLALCHEMY_DATABASE_URI"))
    })


def init_logger():
    logger = getLogger()
    logger.setLevel(INFO)

    fmt = Formatter("%(asctime)s [%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
    sh = StreamHandler()
    sh.setFormatter(fmt)

    logger.addHandler(sh)


def e(message: str) -> None:
    logger = getLogger()
    logger.info(message)


def main():
    def delete_all(vote_id):
        session.query(Vote).filter_by(
            id=vote_id
        ).delete()
        session.query(Session).filter_by(
            vote_id=vote_id
        ).delete()
        session.query(Option).filter_by(
            vote_id=vote_id
        ).delete()

        session.commit()

    a = time()
    session = sessionmaker(bind=engine)()

    now = datetime.now()

    total_votes = session.query(Vote).count()
    deleted_votes = 0
    page = 5
    total_pages = getattr(__import__("math"), "ceil")(total_votes / page)

    e(f"total_votes   = {total_votes}")

    last_id = 0
    for index in range(0, total_pages):
        for v in session.query(Vote).filter(Vote.id > last_id).limit(page).all():
            last_id = v.id
            if type(v.started) == bool:
                if now - v.creation_date > timedelta(hours=3):
                    delete_all(vote_id=v.id)
                    deleted_votes += 1
            else:
                if now - v.finished_date > timedelta(hours=1):
                    delete_all(vote_id=v.id)
                    deleted_votes += 1

    e(f"deleted_votes = {deleted_votes}")
    e(f"elapsed time  = {round(time() - a, 2)}s")
    wait()


def wait():
    try:
        sleep(timedelta(minutes=30).seconds)
        main()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    init_engine()
    init_logger()

    e("===== worker  started =====")
    main()
    e("===== worker finished =====")
