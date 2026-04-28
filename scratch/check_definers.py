import os
import MySQLdb
import MySQLdb.cursors
from dotenv import load_dotenv

load_dotenv('dacd/.env')

def check_definers():
    try:
        conn = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='hola123',
            db='global_security'
        )
        cursor = conn.cursor()
        
        print("Checking for objects with invalid definers in global_security...")
        
        # Check Procedures and Functions
        cursor.execute("""
            SELECT ROUTINE_NAME, DEFINER, ROUTINE_TYPE
            FROM information_schema.ROUTINES 
            WHERE DEFINER LIKE '%bart100%'
            AND ROUTINE_SCHEMA = 'global_security'
        """)
        
        routines = cursor.fetchall()
        for routine in routines:
            print(f"Found {routine[2]}: {routine[0]} with DEFINER: {routine[1]}")
            cursor.execute(f"SHOW CREATE {routine[2]} `{routine[0]}`")
            create_sql = cursor.fetchone()
            print(f"--- Definition for {routine[0]} ---")
            print(create_sql[2])
            print("-----------------------------------")

        # Check Views
        cursor.execute("""
            SELECT TABLE_NAME, DEFINER
            FROM information_schema.VIEWS
            WHERE DEFINER LIKE '%bart100%'
            AND TABLE_SCHEMA = 'global_security'
        """)
        views = cursor.fetchall()
        for view in views:
            print(f"Found VIEW: {view[0]} with DEFINER: {view[1]}")
            cursor.execute(f"SHOW CREATE VIEW `{view[0]}`")
            create_sql = cursor.fetchone()
            print(f"--- Definition for {view[0]} ---")
            print(create_sql[1])
            print("-----------------------------------")

        # Check Triggers
        cursor.execute("""
            SELECT TRIGGER_NAME, DEFINER
            FROM information_schema.TRIGGERS
            WHERE DEFINER LIKE '%bart100%'
            AND TRIGGER_SCHEMA = 'global_security'
        """)
        triggers = cursor.fetchall()
        for trigger in triggers:
            print(f"Found TRIGGER: {trigger[0]} with DEFINER: {trigger[1]}")
            cursor.execute(f"SHOW CREATE TRIGGER `{trigger[0]}`")
            create_sql = cursor.fetchone()
            print(f"--- Definition for {trigger[0]} ---")
            print(create_sql[2])
            print("-----------------------------------")

        if not routines:
            print("No routines found with bart100 definer in global_security.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_definers()
