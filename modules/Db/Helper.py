from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

engine = create_engine('postgres://postgres:otsosika@142.93.5.201:5432/qtracks', pool_size=20, max_overflow=0, pool_pre_ping=True, pool_recycle=3600)
# engine = create_engine('postgres://postgres:otsosika@localhost:5432/qtracks')

Session = scoped_session(sessionmaker(bind=engine))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    password_hash = Column(String)
    account_number = Column(Integer)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Pricing(Base):
    __tablename__ = "pricing"
    id = Column(Integer, primary_key=True)
    underlying = Column(Float)
    symbolId = Column(String(25))
    delta = Column(Float)
    bidPrice = Column(Float)
    bidSize = Column(Float)
    bidMarket = Column(Float)
    askPrice = Column(Float)
    askSize = Column(Float)
    askMarket = Column(Float)
    ivAtBid = Column(Float)
    ivAtAsk = Column(Float)
    strikes = Column(String)
    ivBidMarket = Column(String)
    ivAskMarket = Column(String)
    ivBidFit = Column(String)
    ivAskFit = Column(String)
    comment = Column(String)
    timestamp = Column(DateTime)

