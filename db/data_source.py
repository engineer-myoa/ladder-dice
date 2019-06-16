from sqlalchemy import create_engine


class DataSource:

    engine = None
    def __init__(self):
        self.engine = create_engine("sqlite:///dice.db")
