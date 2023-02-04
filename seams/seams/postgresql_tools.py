import streamlit as st
import psycopg2
from psycopg2 import sql
from seams.datamodels import Users


def db_table_exist(table_name:str)->bool:
    """Checks if `table_name` exists in the database

    Args:
        table_name (str): Name of the table to check if exist in database

    Returns:
        bool: True if `table_name` exist else False
    """
    def error(table_name)->bool:
        st.error(f'Table `{table_name}` does not exist in the database')
        return False 

    tables = db_get_tables_names()
    if tables:
        if table_name in tables:
            return True 
        else:
            return error(table_name)
    else:
        return error(table_name)
        
   
def db_show_all_surveys_stations_tables(lst: list, search_text:str = "stations__"):
    """Returns a list of all the survey stations tables. 

    Args:
        lst (list): list of tables names
        search_text (str, optional): prefix to search for the name of tables with stations for all surveys. Defaults to "stations__".

    Returns:
        list: list with table names of surveys stations. `stations__<surveyID>`
    """
    return [item for item in lst if search_text in item]


def db_get_tables_names():
    """
    This function retrieves the names of all tables in a postgresql database.
    It connects to the database using the psycopg2 library and execute a query to 
    retrieve the table names from the "information_schema.tables" table.
    The result is filtered by the table_schema 'public'.

    Returns:
    - A list of strings, each string representing the name of a table in the database.
    """
    try:
        with psycopg2.connect(**st.secrets['postgres']) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT table_name FROM information_schema.tables
                               WHERE table_schema='public'""")
                tables = cur.fetchall()
                return [table[0] for table in tables]
    except psycopg2.Error as e:
        st.error(f'Error: {e}')
    
                

def db_get_table_schema(table_name:str):
    """
    This function fetches the schema of a table in a postgresql database.
    It connects to the database using the psycopg2 library and execute a query to 
    retrieve the column names, data types and whether they allow null values or not
    from the "information_schema.columns" table.
    The result is filtered by the table name given as input.

    Parameters:
    - table_name (str): name of the table whose schema is to be fetched.

    Returns:
    - A list of strings, each string representing the schema of a column in the table.
    """
    try:
        with psycopg2.connect(**st.secrets['postgres']) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT column_name, data_type, is_nullable
                               FROM information_schema.columns
                               WHERE table_name=%s""", (table_name,))
                schema = cur.fetchall()
                return [f'{column[0]} {column[1]} {column[2]}' for column in schema]
    except psycopg2.Error as e:
        st.error(f'Error: {e}')


def db_delete_table(table_name: str):
    """
    Deletes a table from the database.
    
    Args:
        table_name (str): The name of the table to be deleted.
    """
    # check if table name is not empty
    if not table_name:
        raise ValueError("Table name cannot be empty")
    # check if table name is not a SQL injection attack
    if any(char.isalnum() for char in table_name) == False:
        raise ValueError("Table name cannot contain special characters")
    # connect to the database
    with psycopg2.connect(**st.secrets['postgres']) as conn:
        with conn.cursor() as cur:
            # check if table exists
            cur.execute("""SELECT table_name FROM information_schema.tables
                        WHERE table_schema='public'""")
            tables = cur.fetchall()
            if table_name not in [table[0] for table in tables]:
                raise ValueError(f"Table {table_name} does not exist in the database")
            # drop table
            cur.execute(f"DROP TABLE {table_name}")
            conn.commit()
            return True


def db_create_users_table() -> None:
    """
    This function will create a 'Users' table in the database, with the following columns:
    name, email, affiliation. 
    It will only create the table if it does not exist.
    """
    try:            
        with psycopg2.connect(**st.secrets['postgres']) as conn:
            with conn.cursor() as cur:
                # check if the table exists
                cur.execute("""SELECT table_name FROM information_schema.tables
                            WHERE table_schema='public' AND table_name='users'""")
                table_exists = cur.fetchone()

                if table_exists is None:
                    # create table
                    table_name = sql.Identifier("users")
                    column1 = sql.Identifier("name")
                    column2 = sql.Identifier("email")
                    column3 = sql.Identifier("affiliation")
                    create_table = sql.SQL("CREATE TABLE {} ( {} varchar(255) NOT NULL, {} varchar(255) NOT NULL, {} varchar(255) NOT NULL);").format(table_name, column1, column2, column3)
                    cur.execute(create_table)
                    conn.commit()
                    st.success("Users table created successfully.")
                else:
                    st.warning("Users table already exists.")
    except psycopg2.Error as e:
        st.error(f'Error: {e}')



##----------
def db_insert_new_user(user: Users):
    """Inserts a new user into the Users table in the database

    Args:
        user (Users): an instance of the Users Pydantic model

    Returns:
        bool: True if the user was successfully inserted, False otherwise

    """
    #cur.execute(f"INSERT INTO Users(name, email, affiliation) VALUES (%s, %s, %s)", (user.name, user.email, user.affiliation))

    try:
        with psycopg2.connect(**st.secrets['postgres']) as conn:
            with conn.cursor() as cur:
                # validate the user input
                user_data = user.dict()
                name = user_data.get("name")
                email = user_data.get("email")
                affiliation = user_data.get("affiliation")
                if not all([name, email, affiliation]):
                    raise ValueError("All fields are required.")
                
                # prevent SQL injection attack
                name = sql.Identifier(name).as_string(conn)
                email = sql.Identifier(email).as_string(conn)
                affiliation = sql.Identifier(affiliation).as_string(conn)

                # check if the user already exists
                cur.execute(f"SELECT name FROM users WHERE name='{name}' AND email='{email}'")
                if cur.fetchone():
                    raise ValueError(f"User with name '{name}' and email '{email}' already exists.")
                
                # insert the user data into the table
                cur.execute(f"INSERT INTO Users(name, email, affiliation) VALUES ('{name}', '{email}', '{affiliation}')")
                conn.commit()
                return True
    except (psycopg2.Error, ValueError) as e:
        st.error(e)
        return False



def db_get_users_list():
    """
    This function retrieves the list of users' names from the "Users" table in a postgresql database.
    It connects to the database using the psycopg2 library and execute a query to 
    retrieve the name column from the "Users" table.

    Returns:
    - A list of strings, each string representing a name of a user in the "Users" table.
    """
    try:
        with psycopg2.connect(**st.secrets['postgres']) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name from Users")
                results = cur.fetchall()
                users_list =  [user[0] for user in results]

                return users_list

    except psycopg2.Error as e:
        st.error(f'Error: {e}')


def db_delete_user_by_name(name: str):
    try:
        with psycopg2.connect(**st.secrets['postgres']) as conn:
            with conn.cursor() as cur:
                # validate input to prevent SQL injection
                 # prevent SQL injection attack
                name = sql.Identifier(name).as_string(conn)

                # check if user exists in the table
                cur.execute(f"SELECT name FROM Users WHERE name = %s", (name,))
                result = cur.fetchone()
                if not result:
                    st.error(f"User with name '{name}' not found in the Users table.")
                    return

                cur.execute(f"DELETE FROM Users WHERE name = %s", (name,))
                conn.commit()
                st.success(f"User with name '{name}' has been deleted.")

    except psycopg2.Error as e:
        st.error(e)


def db_delete_users():
    users = db_get_users_list()
    if users:
        selected_users = st.multiselect(label='**DELETE** select users (***WARNING: Action irreversible***)', options=users, )
        with st.spinner('DELETING IN PROGRESS...'):
            for user in selected_users:
                db_delete_user_by_name(user.replace('"',""))
    else:
        st.warning('No users registered in the database')

def db_select_user_by_name(name: str):
    try:
        with psycopg2.connect(**st.secrets['postgres']) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM Users WHERE name='{name}'")
                result = cur.fetchone()
                conn.commit()
                return result
    except Exception as e:
        st.error(f"Error: {e}")
        return None







