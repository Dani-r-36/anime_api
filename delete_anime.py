import psycopg2
import psycopg2.extras 

DELETE_CREATE_ANIME_SQL ="""
drop table if exists animes;
create table if not exists animes (
	animes_id INT generated always as identity,
	anime VARCHAR(100) not null,
	start_date_id INT not null,
	end_date_id INT not null,
	show_type_id INT not null,
	episodes INT not null,
	score FLOAT not null,
	primary key (animes_id),
	foreign key (start_date_id) references dates(dates_id),
	foreign key (end_date_id) references dates(dates_id),
	foreign key (show_type_id) references show_type(show_type_id)
);"""

def restart_animes_table(conn):
    try:
        with conn.cursor() as cur:
            cur.execute(DELETE_CREATE_ANIME_SQL, )
    except Exception as err:
        print(err)
        print(err, "Could not delete anime table.")
    finally:
        conn.commit()
