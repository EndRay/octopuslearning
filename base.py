from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Performance(Base):
    __tablename__ = 'performances'
    contestId = Column(Integer, primary_key=True)
    handle = Column(String, primary_key=True)
    oldRating = Column(Integer)
    points = Column(Integer)
    penalty = Column(Integer)

# class Contest(Base):
#     __tablename__ = 'contests'
#     contestId = Column(Integer, primary_key=True)
#     startTimeSeconds = Column(Integer)
#     name = Column(String)
#     durationSeconds = Column(Integer)


engine = create_engine('sqlite:///codeforces.sqlite')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)  # once engine is available
session = Session()
