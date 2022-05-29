#!/usr/bin/env python3
from os import environ
from time import time
from time import sleep
from sched import scheduler
from functools import wraps
from datetime import datetime
from datetime import timedelta
from logging import INFO
from logging import getLogger
from logging import StreamHandler
from logging import Formatter

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Vote
from app.models import Session
from app.models import Option

logger = getLogger()
s = scheduler(time, sleep)
schedule = {}


def register_schedule(delay: int):
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            s.enter(**schedule[f.__name__])
            return f(*args, **kwargs)

        schedule.update({
            f.__name__: {
                "delay": delay,
                "priority": 1,
                "action": decorator
            }
        })

        decorator()
        return decorator
    return wrapper


def main():
    @register_schedule(timedelta(minutes=10).seconds)
    def clear_vote():
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

        session = sessionmaker(bind=engine)()

        now = datetime.now()

        total_votes = session.query(Vote).count()
        deleted_votes = 0
        per_page = 5
        total_pages = getattr(__import__("math"), "ceil")(total_votes / per_page)

        logger.info(f"total votes : {total_pages}")
        logger.info(f"total pages : {total_pages}")

        last_id = 0
        for index in range(0, total_pages):
            for v in session.query(Vote).filter(Vote.id > last_id).limit(per_page).all():
                last_id = v.id
                if type(v.started) == bool:
                    if now - v.creation_date > timedelta(hours=3):
                        delete_all(vote_id=v.id)
                        deleted_votes += 1
                else:
                    if now - v.finished_date > timedelta(hours=1):
                        delete_all(vote_id=v.id)
                        deleted_votes += 1

        logger.info(f"{deleted_votes} votes deleted")


if __name__ == "__main__":
    load_dotenv()
    logger.setLevel(INFO)
    handler = StreamHandler()
    handler.setFormatter(fmt=Formatter("%(asctime)s [%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(hdlr=handler)

    engine = create_engine(environ.get("SQLALCHEMY_DATABASE_URI"))
    session_factory = sessionmaker(bind=engine)

    main()

    try:
        s.run()
    except KeyboardInterrupt:
        logger.info("exited!")
