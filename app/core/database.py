import psycopg


def connect_to_database(
    host: str,
    port: int,
    database: str,
    username: str,
    password: str,
):
    return psycopg.connect(
        host=host,
        port=port,
        dbname=database,
        user=username,
        password=password,
    )
