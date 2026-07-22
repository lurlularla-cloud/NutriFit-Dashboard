"""
각 데이터셋(iherb, oliveyoung, coupang)의 CSV 및 DB 데이터를 분석하여
통합에 필요한 컬럼 매핑과 데이터 형식을 파악하는 스크립트입니다.
"""
import pandas as pd
import sqlite3
import os

def check_csv(path, name):
    print(f"\n=== CSV: {name} ({path}) ===")
    if not os.path.exists(path):
        print("파일이 존재하지 않습니다.")
        return
    try:
        df = pd.read_csv(path, nrows=5)
        print("Columns:", list(df.columns))
        print("Sample Row 0:")
        print(df.iloc[0].to_dict() if len(df) > 0 else "Empty")
        
        # 전체 행 수 확인
        df_full = pd.read_csv(path, usecols=[0])
        print(f"Total Rows: {len(df_full)}")
    except Exception as e:
        print("Error:", e)

def check_db(path, name):
    print(f"\n=== DB: {name} ({path}) ===")
    if not os.path.exists(path):
        print("파일이 존재하지 않습니다.")
        return
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", [t[0] for t in tables])
        for table in tables:
            tname = table[0]
            cursor.execute(f"PRAGMA table_info({tname});")
            cols = cursor.fetchall()
            print(f"  Table '{tname}' Columns:", [c[1] for c in cols])
            cursor.execute(f"SELECT COUNT(*) FROM {tname};")
            count = cursor.fetchone()[0]
            print(f"  Total Rows in '{tname}': {count}")
            cursor.execute(f"SELECT * FROM {tname} LIMIT 1;")
            row = cursor.fetchone()
            print(f"  Sample Row in '{tname}': {row}")
        conn.close()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    # 1. iherb
    check_csv("iherb/data/서동임_Herb_supplements (1).csv", "iherb_supplements")
    check_csv("iherb/data/iherb_specials.csv", "iherb_specials")
    
    # 2. oliveyoung
    check_csv("oliveyoung/data/서동임_올리브영_건강식품_수집데이터.csv", "oliveyoung_health_csv")
    check_csv("oliveyoung/data/올리브영_비타민_수집데이터.csv", "oliveyoung_vitamin")
    check_db("oliveyoung/data/oliveyoung_health.db", "oliveyoung_health_db")
    
    # 3. coupang
    check_csv("coupang/data/coupang_all_products.csv", "coupang_all_products")
    check_db("coupang/data/coupang.db", "coupang_db")
