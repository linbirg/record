#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# MySQL → SQLite 全量迁移脚本

import os
import sys

__abs_file__ = os.path.abspath(__file__)
tool_dir = os.path.dirname(__abs_file__)
code_dir = os.path.dirname(tool_dir)
sys.path.append(code_dir)

import pymysql
import sqlite3
from conf import db as db_conf


TABLES = [
    {
        'name': 'user',
        'columns': 'user_id, user_name, nickname, password, created_at, updated_at'
    },
    {
        'name': 'note_risk',
        'columns': 'id, user_id, user_name, reg_date, week_count, job, new_job, risk, risk_solve_time, updated_at, created_at'
    },
    {
        'name': 't_week_note',
        'columns': 'id, user_id, user_name, week_count, week_day, rec_date, year, updated_at, created_at'
    },
    {
        'name': 't_note_detail',
        'columns': 'id, note_id, user_id, user_name, rec_date, week_day, status, job, updated_at, created_at'
    },
    {
        'name': 't_car_info',
        'columns': 'id, user_name, dept, carid, seq_no, reg_date, brand, car_license, license, abbr, updated_at, created_at'
    },
    {
        'name': 't_car_pics',
        'columns': 'id, car_id, path, updated_at, created_at'
    },
    {
        'name': 't_chat_message',
        'columns': 'id, user_id, session_id, role, content, created_at'
    },
]


def get_mysql_connection():
    return pymysql.connect(
        host=db_conf.rec_db.get('host'),
        port=db_conf.rec_db.get('port'),
        user=db_conf.rec_db.get('user'),
        password=db_conf.rec_db.get('password'),
        db=db_conf.rec_db.get('db'),
        charset='utf8mb4'
    )


def get_sqlite_connection():
    return sqlite3.connect(db_conf.SQLITE_DB_PATH)


def migrate_table(mysql_conn, sqlite_conn, table_info):
    table_name = table_info['name']
    columns = table_info['columns']
    col_list = [c.strip() for c in columns.split(',')]

    mysql_cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)

    try:
        mysql_cursor.execute(f"SELECT {columns} FROM {table_name}")
        rows = mysql_cursor.fetchall()

        if not rows:
            return 0

        sqlite_cursor = sqlite_conn.cursor()

        placeholders = ','.join(['?' for _ in col_list])
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        data_rows = []
        for row in rows:
            values = []
            for col in col_list:
                val = row.get(col)
                if val is None:
                    val = ''
                elif isinstance(val, (bytes, bytearray)):
                    val = val.decode('utf-8', errors='ignore')
                elif hasattr(val, 'isoformat'):
                    val = val.isoformat()
                elif isinstance(val, bool):
                    val = 1 if val else 0
                elif isinstance(val, int) and not isinstance(val, bool):
                    pass
                else:
                    val = str(val)
                values.append(val)
            data_rows.append(tuple(values))

        sqlite_cursor.executemany(insert_sql, data_rows)

        return len(data_rows)

    finally:
        mysql_cursor.close()


def main():
    print("=== MySQL → SQLite 数据迁移 ===")
    print(f"MySQL: {db_conf.rec_db.get('host')}:{db_conf.rec_db.get('port')}/{db_conf.rec_db.get('db')}")
    print(f"SQLite: {db_conf.SQLITE_DB_PATH}")
    print()

    mysql_conn = None
    sqlite_conn = None

    try:
        print("连接数据库...")
        mysql_conn = get_mysql_connection()
        sqlite_conn = get_sqlite_connection()

        print("禁用 SQLite 外键约束...")
        sqlite_conn.execute("PRAGMA foreign_keys = OFF")

        print("开启事务...")
        sqlite_conn.execute("BEGIN TRANSACTION")

        total_rows = 0

        for i, table in enumerate(TABLES, 1):
            table_name = table['name']
            print(f"[{i}/{len(TABLES)}] 迁移 {table_name} 表...", end=' ', flush=True)

            rows = migrate_table(mysql_conn, sqlite_conn, table)
            print(f"{rows} rows")

            total_rows += rows

        print()
        print("提交事务...")
        sqlite_conn.commit()

        print("恢复外键约束...")
        sqlite_conn.execute("PRAGMA foreign_keys = ON")

        print()
        print(f"迁移完成！总计: {total_rows} rows")

    except Exception as e:
        print()
        print(f"迁移失败: {e}")
        if sqlite_conn:
            print("回滚事务...")
            sqlite_conn.rollback()
        raise

    finally:
        if mysql_conn:
            mysql_conn.close()
        if sqlite_conn:
            sqlite_conn.close()


if __name__ == '__main__':
    main()
