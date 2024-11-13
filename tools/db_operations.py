from pydantic import BaseModel


def create_insert_query(obj: BaseModel, table: str) -> str:
    obj_keys = [key for key, _ in obj.__dict__.items()]
    col_string = ", ".join(obj_keys)
    val_string = "%(" + ")s, %(".join(obj_keys) + ")s"
    query = f"""
                    INSERT INTO {table}({col_string})
                    VALUES ({val_string});
                    """
    return query


def insert_item(obj: BaseModel, table: str, cur):
    query = create_insert_query(obj, table)
    return cur.execute(query, obj.__dict__)


def create_retrieve_query(key: str, table: str, where: str | None) -> str:
    query = f"SELECT {key} FROM {table}"
    if where is not None:
        query = query + f" WHERE {where}"
    return query


def retrieve_items(key: str, table: str, cur, where: str | None = None) -> list:
    query = create_retrieve_query(key, table, where)
    tuples = cur.execute(query).fetchall()
    return [item[0] for item in tuples]
