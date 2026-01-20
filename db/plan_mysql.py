import pymysql as mysql
from pymysql.cursors import DictCursor
from pymysql import IntegrityError
from datetime import datetime
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

load_dotenv()
# print("DB_PORT =", os.getenv("DB_PORT"))


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user" : os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
}
# 여행 일정 저장
def create_plan(title :str, description : str, plan: str,  start_date:str, end_date:str):
    try:
        con = mysql.connect(**DB_CONFIG, cursorclass=DictCursor)
        cursor = con.cursor()

        sql = """
        INSERT INTO trips (title, description, plan, createdAt, start_date, end_date)
        VALUES (%s, %s, %s, now(), %s, %s)
        """

        cursor.execute(
            sql,(title, description, plan, start_date, end_date )
        )

        con.commit()
        con.close()

        print("✅ trips-plan 저장 완료")

    except IntegrityError as e:
        print("❌ DB 무결성 에러", e)
        raise
    except Exception as e:
        print("❌ DB 에러", e)
        raise


# 여행 일정 조회 (전체)
def read_plan_last():
    try:
        con = mysql.connect(**DB_CONFIG, cursorclass=DictCursor)
        cursor = con.cursor()

        sql = "SELECT id FROM trips ORDER BY id DESC limit 1"
        cursor.execute(sql)
        row = cursor.fetchone()

        print(row)

        con.close()
        return row['id']

    except Exception as e:
        print("❌ 조회 에러", e)
        raise

# 여행 일정 저장
def create_usertrip(userId : int, tripId: int):
    try:
        con = mysql.connect(**DB_CONFIG, cursorclass=DictCursor)
        cursor = con.cursor()

        sql = """
        INSERT INTO usertrip (Owner, UserId, TripId)
        VALUES (1, %s, %s)
        """

        cursor.execute(
            sql,(userId, tripId)
        )

        con.commit()
        con.close()

        print("✅ usertrip 저장 완료")

    except IntegrityError as e:
        print("❌ DB 무결성 에러", e)
        raise
    except Exception as e:
        print("❌ DB 에러", e)
        raise


# 여행 일정 조회 (전체)
def read_plan_all():
    try:
        con = mysql.connect(**DB_CONFIG, cursorclass=DictCursor)
        cursor = con.cursor()

        sql = "SELECT * FROM trips ORDER BY createdAt DESC"
        cursor.execute(sql)
        rows = cursor.fetchall()

        con.close()
        return rows

    except Exception as e:
        print("❌ 조회 에러", e)
        raise


# 여행 일정 단건 조회
def read_plan_by_id(trip_id: int):
    try:
        con = mysql.connect(**DB_CONFIG, cursorclass=DictCursor)
        cursor = con.cursor()

        sql = "SELECT * FROM trips WHERE id = %s"
        cursor.execute(sql, (trip_id,))
        row = cursor.fetchone()

        con.close()
        return row

    except Exception as e:
        print("❌ 조회 에러", e)
        raise
