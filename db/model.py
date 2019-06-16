from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from . import data_source
import datetime

Base = declarative_base()
dataSource = data_source.DataSource()


class DiceMember(Base):
    __tablename__ = "DICE_MBR"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=20))
    reg_dtime = Column(DateTime)

    def __init__(self, name):
        self.name = name
        self.reg_dtime = datetime.datetime.now()

    def __repr__(self):
        return "<DiceMember(id='%s', name='%s', reg_dtime='%s')>" % (self.id, self.name, self.reg_dtime)


class DiceResult(Base):
    __tablename__ = "DICE_RSLT"

    seq = Column(Integer, primary_key=True, autoincrement=True)
    raw_result = Column(String(length=4000))
    rslt_id = Column(String(length=20))
    reg_dtime = Column(DateTime)

    def __init__(self, raw_result, rslt_id):
        self.raw_result = raw_result
        self.rslt_id = rslt_id
        self.reg_dtime = datetime.datetime.now()

    def __repr__(self):
        return "<DiceResult(seq='%s', raw_result='%s', rslt_id='%s', reg_dtime='%s')>"\
               % (self.seq, self.raw_result, self.rslt_id, self.reg_dtime)


Base.metadata.create_all(dataSource.engine)