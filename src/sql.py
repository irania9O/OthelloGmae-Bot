import sqlite3
import pickle
import time

sqlite3.register_converter("pickle", pickle.loads)

class SaveKeyboard:

    def __init__(self) -> None:
        self.conn = sqlite3.connect('src/database.db', detect_types=sqlite3.PARSE_DECLTYPES)
        self.c = self.conn.cursor()

        self.c.execute("""
            CREATE TABLE IF NOT EXISTS BOARDS (
                MSG_ID      TEXT        NOT NULL,
                CHT_ID      TEXT        NOT NULL,
                EN_NAME      TEXT        NOT NULL,
                MY_NAME      TEXT        NOT NULL,
                DATA        pickle,
                TIME        INT         DEFAULT 0,
                PRIMARY KEY (MSG_ID, CHT_ID)
                )""")

    def insert_into_db(self, MSG_ID, CHT_ID, MY_NAME, EN_NAME, obj):
        try:
            pdata = pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
            self.c.execute(
                "insert into BOARDS (MSG_ID, CHT_ID, DATA, TIME, MY_NAME, EN_NAME) values (:MSG_ID, :CHT_ID, :DATA, :TIME, :MY_NAME, :EN_NAME)", 
                (str(MSG_ID), str(CHT_ID), sqlite3.Binary(pdata), int(time.time()), str(MY_NAME), str(EN_NAME))
            )
        except Exception as e:
            print(e)

        self.conn.commit()

    def update_keyboard(self, MSG_ID, CHT_ID, obj):
        try:
            pdata = pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
            self.c.execute(
                f"UPDATE BOARDS SET DATA = :DATA WHERE MSG_ID = :MSG_ID AND CHT_ID = :CHT_ID",
                (sqlite3.Binary(pdata), str(MSG_ID), str(CHT_ID))
            )
        except Exception as e:
            print(e)

        self.conn.commit()


    def get_obj_from_db(self, MSG_ID, CHT_ID):
        self.c.execute(f"select * from BOARDS where `MSG_ID` = '{MSG_ID}' and `CHT_ID` = '{CHT_ID}'")
        for row in self.c:
            return row

    def delete_obj(self, MSG_ID, CHT_ID):
        try:
            self.c.execute(
                f"DELETE FROM BOARDS WHERE MSG_ID = :MSG_ID AND CHT_ID = :CHT_ID",
                (str(MSG_ID), str(CHT_ID))
            )
        except Exception as e:
            print(e)

    def delete_obj_all(self):
        time_c = time.time() - 2 * 60 * 60 
        try:
            self.c.execute(
                f"DELETE FROM BOARDS WHERE TIME < {time_c}",
            )
        except Exception as e:
            print(e)

        self.conn.commit()
manage = SaveKeyboard()
manage.delete_obj_all()