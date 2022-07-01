from os import environ
from sys import argv
from math import ceil
from time import sleep
from secrets import token_hex
from datetime import datetime

from uvicorn import run
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from app import app as __app__
from sql import get_session
from sql.models import Vote
from sql.models import VoteSession
from sql.models import VoteOption

if __name__ == "__main__":
    def vote_clean_up():
        item_in_page = 20
        session = get_session()
        filters = datetime.now() > Vote.deleted_at

        length = session.query(Vote).filter(filters).count()
        total_page = ceil(length / item_in_page)

        for page in range(1, total_page + 1):
            for vote in session.query(Vote).filter(filters) \
                    .offset(item_in_page * (page - 1)).limit(item_in_page).all():
                session.query(VoteOption).filter_by(vote_id=vote.id).delete()
                session.query(VoteSession).filter_by(vote_id=vote.id).delete()
                session.delete(vote)
                session.commit()

            sleep(5)

        session.close()

    # import env
    load_dotenv()

    # set up scheduler
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.start()
    scheduler.add_job(
        func=vote_clean_up,
        trigger="cron",
        id="vote_clean_up",
        name="remove expired vote",
        # kwargs
        hour="*/1",
    )

    # set jwt secret
    if "--dev" in argv:
        key = "chick_0"
    else:
        key = token_hex(48)

    environ.__setitem__("JWT_SECRET", key)

    run(
        app=__app__,
        host="127.0.0.1",
        port=28282,
        log_level="info",
        #
        workers=1
    )
