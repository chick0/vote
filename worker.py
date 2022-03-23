from os import environ
from datetime import datetime
from datetime import timedelta

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


def e(message: str) -> None:
    print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), message)


def main():
    session = sessionmaker(bind=engine)()

    now = datetime.now()
    ttl = timedelta(days=1)

    total_votes = session.query(Vote).count()
    page = 5
    total_pages = getattr(__import__("math"), "ceil")(total_votes / page)

    e(f"total_votes = {total_votes}")
    e(f"total_pages = {total_pages}")

    last_id = 0
    for index in range(0, total_pages):
        for v in session.query(Vote).filter(Vote.id > last_id).limit(page).all():
            last_id = v.id

            if now - v.creation_date > ttl:
                e(f"vote id({v.id}) is expired")

                session.query(Vote).filter_by(
                    id=v.id
                ).delete()
                session.query(Session).filter_by(
                    vote_id=v.id
                ).delete()
                session.query(Option).filter_by(
                    vote_id=v.id
                ).delete()

                session.commit()

    e("finished!")


if __name__ == "__main__":
    init_engine()
    main()
