import psycopg2
import psycopg2.extras 
from dotenv import dotenv_values

from anime_scraper import top_anime_extract, parse_anime

def get_db_connection():
    """establishes connection to database"""
    try:
        config = dotenv_values('.env')
        connection = psycopg2.connect( user = config["DATABASE_USERNAME"], password = config["DATABASE_PASSWORD"], host = config["DATABASE_HOST"], port = config["DATABASE_PORT"], database = config["DATABASE_NAME"]) 
        return connection
    except:
        print("Error connecting to database.")

conn = get_db_connection()

def adding_animes(anime_titles, start_id, end_id, show_type_id, episodes, score):
    """carrys out insert for database"""
    try:
        curs= conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        current_date = 5
        # curs.execute(" ALTER SEQUENCE stories_id_seq RESTART WITH 1;")
        for index, anime in enumerate(anime_titles):
            print("before insert")
            print(anime,start_id[index],end_id[index],show_type_id[index],episodes[index],score[index])
            sql_insert_data("""INSERT INTO animes (anime, start_date_id, end_date_id, show_type_id, episodes, score)
            VALUES (%s, %s, %s, %s, %s, %s);""",[anime, start_id[index], end_id[index], show_type_id[index], episodes[index], score[index]])
            print("inserted")
    except Exception as err:
        print (err)
        return error_message("Error in inserting data",'')


def adding_repeated_info(list_data, type_addition):
    """inserts and gets ids of tags which are being scrapped"""
    try:
        column = ""
        if type_addition == "dates":
            column = "year"
        else:
            column = "type"
        curs= conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
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
    """returns the id of inserted or existing tag"""
    data = sql_execute(f"SELECT {type_addition}.{type_addition}_id FROM {type_addition} WHERE {type_addition}.{column} =%s",[date_year])
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
    """handles most sql inserts"""
    curs = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    curs.execute(sql, params)
    conn.commit()
    curs.close()

ADDRESS_SQL = """WITH ins AS (
  INSERT INTO rider_address 
  (house_no, street_name, city, postcode) 
  VALUES (%s, %s, %s, %s)
  ON CONFLICT DO NOTHING
  RETURNING address_id
)
SELECT address_id FROM ins
UNION ALL
SELECT address_id FROM rider_address
WHERE house_no = %s
  AND street_name = %s
  AND city = %s
  AND postcode = %s;"""

def restart_animes_table():
    try:
        with conn.cursor() as cur:
            cur.execute(ADDRESS_SQL, [rider_address['house_no'],
                                    rider_address['street_name'],
                                    rider_address['city'],
                                    rider_address['postcode'],
                                    rider_address['house_no'],
                                    rider_address['street_name'],
                                    rider_address['city'],
                                    rider_address['postcode']])
            address_id = cur.fetchall()[0][0]
    except Exception as err:
        print(err)
        print(err, "Could not add rider address to the database.")
    finally:
        conn.commit()
    return address_id


if __name__ == "__main__":
    top = parse_anime("https://myanimelist.net/topanime.php")
    anime_list, anime_urls, type_list, eps_list, start_list, end_list, score_list = top_anime_extract(top)
    anime_year = start_list + end_list
    start_id = adding_repeated_info(start_list, "dates")
    end_id = adding_repeated_info(end_list, "dates")
    show_type_id = adding_repeated_info(type_list, "show_type")
    print("calling")
    temp = adding_animes(anime_list, start_id, end_id, show_type_id, eps_list, score_list)
    print(temp)