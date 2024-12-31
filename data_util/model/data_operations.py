from sqlalchemy import create_engine


def get_engine(connection_string: str):
    if not connection_string:
        return None
    else:
        engine = create_engine(connection_string)
        return engine
