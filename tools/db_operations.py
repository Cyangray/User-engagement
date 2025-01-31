import psycopg
from pydantic import BaseModel
import pandas as pd


def create_insert_query(obj: BaseModel, table: str) -> str:
    """
    helper function that generates an SQL query in order to add a row to an SQL table.
    :param obj: the Pydantic model from which to generate a database row. In this API, it can be a User or Activity object.
    :param table: string. The name of the table where to add the row. In this API, it could be either "users" or "activities".
    :return: the SQL query.
    """
    obj_keys = [key for key, _ in obj.__dict__.items()]
    col_string = ", ".join(obj_keys)
    val_string = "%(" + ")s, %(".join(obj_keys) + ")s"
    query = f"""
                    INSERT INTO {table}({col_string})
                    VALUES ({val_string});
                    """
    return query


def insert_item(obj: BaseModel, table: str, cur: psycopg.Cursor) -> None:
    """
    Helper function that executes the query generated by create_insert_query.
    :param obj: the Pydantic model from which to generate a database row. In this API, it can be a User or Activity object.
    :param table: string. The name of the table where to add the row. In this API, it could be either "users" or "activities".
    :param cur: the cursor for the psycopg connection to be used to execute the SQL query.
    """
    query = create_insert_query(obj, table)
    cur.execute(query, obj.__dict__)
    return None


def create_retrieve_query(key: str, table: str, where: str | None) -> str:
    """
    Helper function that generates a query to retrieve the entries in an SQL table column, given the table name, and the column key.
    :param key: string. The column to extract.
    :param table: string. The name of the table from which to extract the column.
    :param where: string (optional): possible logical conditions to apply for the extraction. Must be written in SQL syntax.
    :return: the SQL query.
    """
    query = f"SELECT {key} FROM {table}"
    if where is not None:
        query = query + f" WHERE {where}"
    return query


def retrieve_items(
    key: str, table: str, cur: psycopg.Cursor, where: str | None = None
) -> list:
    """
    Helper function executing the query generated in create_retrieve_query.
    :param key: string. The column to extract.
    :param table: string. The name of the table from which to extract the column.
    :param cur: the cursor for the psycopg connection to be used to execute the SQL query.
    :param where: string (optional): possible logical conditions to apply for the extraction. Must be written in SQL syntax.
    :return: a list of items extracted from the SQL table.
    """
    query = create_retrieve_query(key, table, where)
    tuples = cur.execute(query).fetchall()
    return [item[0] for item in tuples]


def sql_to_dataframe(table, cur: psycopg.Cursor, where=None):
    query = create_retrieve_query("*", table, where)
    tuples = cur.execute(query).fetchall()
    colnames = [desc[0] for desc in cur.description]
    # Now we need to transform the list into a pandas DataFrame:
    df = pd.DataFrame(tuples)
    for i, colname in enumerate(colnames):
        df.rename(columns={i: colname}, inplace=True)
    return df
