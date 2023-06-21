"""Uploads top 50 data to database"""
import psycopg2
import psycopg2.extras 
from dotenv import dotenv_values
from delete_anime import restart_animes_table
from anime_scraper import top_anime_extract, parse_anime

def get_db_connection():
    """establishes connection to database"""
    try:
        config = dotenv_values('/users/dani/Documents/anime/.env')
        connection = psycopg2.connect( user = config["DATABASE_USERNAME"], password = config["DATABASE_PASSWORD"], host = config["DATABASE_HOST"], port = config["DATABASE_PORT"], database = config["DATABASE_NAME"]) 
        return connection
    except:
        print("Error connecting to database.")

conn = get_db_connection()

def adding_animes(anime_titles, start_id, end_id, show_type_id):
    """carrys out insert of anime for database"""
    try:
        # curs.execute(" ALTER SEQUENCE stories_id_seq RESTART WITH 1;")
        for index, anime in enumerate(anime_titles):
            # print(anime["anime"], anime['position'], start_id[index], end_id[index], show_type_id[index], anime['eps'], anime['score'])
            sql_insert_data("""INSERT INTO animes (anime, start_date_id, end_date_id, show_type_id, episodes, score)
            VALUES (%s, %s, %s, %s, %s, %s);""",[anime["anime"], start_id[index], end_id[index], show_type_id[index], anime['eps'], anime['score']])
    except Exception as err:
        print (err)
        return error_message("Error in inserting data",'')


def adding_repeated_info(list_data, type_addition):
    """inserts dates and type info which are scrapped"""
    try:
        column = ""
        if type_addition == "dates":
            column = "year"
        else:
            column = "type"
        id=[]
        # curs.execute(" ALTER SEQUENCE tags_id_seq RESTART WITH 1;")
        i = 0
        while i < len(list_data):
            data = dates_return_id(list_data[i], type_addition, column)
            if len(data) == 0:
                sql_insert_data(f"INSERT INTO {type_addition} ({column}) VALUES (%s);",[list_data[i]])
                data = dates_return_id(list_data[i], type_addition, column)
            id.append(data[0][f'{type_addition}_id'])
            i +=1
        return id
    except Exception:
        return error_message("Error in inserting tags",'')


def dates_return_id(date_year, type_addition, column):
    """returns the id of inserted or existing dates or type"""
    data = sql_execute(f"SELECT {type_addition}.{type_addition}_id FROM {type_addition} WHERE {type_addition}.{column} =%s",[date_year])
    return data

def get_anime_sql():
    """sql to get top 50 animes"""
    sql_command = """SELECT * FROM animes;"""
    data = sql_execute(sql_command,None)
    return data

def error_message(message,num):
    """handles all error messages"""
    return {"error": True, "Message": message, "Status_code":num}


def sql_execute(sql,params):
    """handles most sql executes"""
    curs = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    curs.execute(sql, params)
    data =curs.fetchall()
    curs.close()
    return data


def sql_insert_data(sql,params):
    """handles sql inserts"""
    curs = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    curs.execute(sql, params)
    conn.commit()
    curs.close()

if __name__ == "__main__":
    restart_animes_table(conn)
    print("deleted table")
    top = parse_anime("https://myanimelist.net/topanime.php")
    anime_list = top_anime_extract(top)
    start_list = [d['start'] for d in anime_list]
    end_list = [d['end'] for d in anime_list] 
    type_list = [d['type_genre'] for d in anime_list]
    start_id = adding_repeated_info(start_list, "dates")
    end_id = adding_repeated_info(end_list, "dates")
    show_type_id = adding_repeated_info(type_list, "show_type")
    temp = adding_animes(anime_list, start_id, end_id, show_type_id)
    print("uploaded new table")