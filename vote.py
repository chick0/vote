from os import environ
from sys import argv
from math import ceil
from time import sleep
from datetime import datetime
from datetime import timedelta
from logging import getLogger
from logging import StreamHandler
from logging import Formatter
from logging import INFO
from logging import WARNING

from waitress import serve
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler

from app import create_app
from app.models import Vote
from app.models import Session
from app.models import Option

logger = getLogger()
scheduler = BackgroundScheduler(timezone="Asia/Seoul")


def init_logger():
    logger.setLevel(INFO)
    handler = StreamHandler()
    handler.setFormatter(fmt=Formatter("%(asctime)s [%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(hdlr=handler)
    getLogger('apscheduler.executors.default').setLevel(WARNING)


def init_scheduler():
    if "SQLALCHEMY_DATABASE_URI" not in environ:
        load_dotenv()

    engine = create_engine(
        url=environ['SQLALCHEMY_DATABASE_URI'],
        pool_size=1,
        max_overflow=1,
    )

    factory = sessionmaker(bind=engine)
    item_in_page = 20

    def get_session():
        return factory()

    @scheduler.scheduled_job(
        "cron",
        hour="*/1",
        id="vote_clean_up",
        name="remove expired vote",
    )
    def vote_clean_up():
        session = get_session()
        filters = Vote.creation_date < datetime.now() - timedelta(hours=6)

        length = session.query(Vote).filter(filters).count()
        total_page = ceil(length / item_in_page)

        for page in range(1, total_page + 1):
            for vote in session.query(Vote).filter(filters) \
                    .offset(item_in_page * (page - 1)).limit(item_in_page).all():
                session.delete(vote)
                session.query(Session).filter_by(
                    vote_id=vote.id
                ).delete()
                session.query(Option).filter_by(
                    vote_id=vote.id
                ).delete()

                session.commit()

            sleep(5)

        session.close()


def main():
    host, port = "127.0.0.1", 28282
    serve(app=create_app(), host=host, port=port, _quiet=False)


if __name__ == "__main__":
    init_logger()
    if "--no-scheduler" not in argv:
        scheduler.start()
        init_scheduler()
    else:
        logger.info("Scheduler disabled")

    main()
