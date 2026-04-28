import MySQLdb
import MySQLdb.cursors
import os
from dotenv import load_dotenv

load_dotenv('dacd/.env')

def generate_fix():
    try:
        conn = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='hola123',
            db='global_security'
        )
        cursor = conn.cursor()
        
        fix_sql_path = 'fix_mysql_objects_full.sql'
        with open(fix_sql_path, 'w', encoding='utf-8') as f:
            f.write("-- Full script to fix ALL 'bart100' definers in global_security\n")
            f.write("-- Replaced with 'root'@'localhost' as requested\n\n")
            f.write("DELIMITER //\n\n")

            # 1. Procedures and Functions
            cursor.execute("""
                SELECT ROUTINE_NAME, ROUTINE_TYPE
                FROM information_schema.ROUTINES 
                WHERE DEFINER LIKE '%bart100%'
                AND ROUTINE_SCHEMA = 'global_security'
            """)
            routines = cursor.fetchall()
            print(f"Processing {len(routines)} routines...")
            for name, rtype in routines:
                cursor.execute(f"SHOW CREATE {rtype} `{name}`")
                res = cursor.fetchone()
                original_sql = res[2]
                
                # Replace DEFINER
                fixed_sql = original_sql.replace('DEFINER=`bart100`@`%`', 'DEFINER=`root`@`localhost`')
                
                f.write(f"DROP {rtype} IF EXISTS `{name}` //\n")
                f.write(f"{fixed_sql} //\n\n")

            f.write("DELIMITER ;\n\n")

            # 2. Views
            cursor.execute("""
                SELECT TABLE_NAME
                FROM information_schema.VIEWS
                WHERE DEFINER LIKE '%bart100%'
                AND TABLE_SCHEMA = 'global_security'
            """)
            views = cursor.fetchall()
            print(f"Processing {len(views)} views...")
            for (name,) in views:
                cursor.execute(f"SHOW CREATE VIEW `{name}`")
                res = cursor.fetchone()
                original_sql = res[1]
                
                # Replace DEFINER
                fixed_sql = original_sql.replace('DEFINER=`bart100`@`%`', 'DEFINER=`root`@`localhost`')
                
                f.write(f"DROP VIEW IF EXISTS `{name}`;\n")
                f.write(f"{fixed_sql};\n\n")

            # 3. Triggers
            cursor.execute("""
                SELECT TRIGGER_NAME
                FROM information_schema.TRIGGERS
                WHERE DEFINER LIKE '%bart100%'
                AND TRIGGER_SCHEMA = 'global_security'
            """)
            triggers = cursor.fetchall()
            print(f"Processing {len(triggers)} triggers...")
            for (name,) in triggers:
                cursor.execute(f"SHOW CREATE TRIGGER `{name}`")
                res = cursor.fetchone()
                original_sql = res[2]
                
                # Replace DEFINER
                fixed_sql = original_sql.replace('DEFINER=`bart100`@`%`', 'DEFINER=`root`@`localhost`')
                
                f.write(f"DROP TRIGGER IF EXISTS `{name}`;\n")
                f.write(f"{fixed_sql};\n\n")

        print(f"Full fix script generated: {fix_sql_path}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_fix()
