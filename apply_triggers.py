import os
import subprocess

config_file = r'c:\Users\kathe\Documents\DAC_D\my.cnf'
database = 'universal_data_core'
sql_files = [
    r'c:\Users\kathe\Documents\DAC_D\TRIGGER_after_devolucion_insert.sql',
    r'c:\Users\kathe\Documents\DAC_D\TRIGGER_after_devolucion_update.sql'
]

for sql_file in sql_files:
    print(f"Processing {os.path.basename(sql_file)}...")
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # We need to remove the DELIMITER lines because mysql client -e or piped input 
        # doesn't always like the DELIMITER command itself, but we'll try it as is first.
        # Actually, many mysql clients handle it fine.
        
        # Try using the -p flag with the alternate password if defaults-extra-file fails
        proc = subprocess.Popen(
            ['mysql', '-u', 'root', '-phola123', database],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = proc.communicate(input=sql_content)
        
        if proc.returncode == 0:
            print(f"Applied {os.path.basename(sql_file)} successfully.")
        else:
            print(f"Error applying {os.path.basename(sql_file)}:")
            print(stderr)
    except Exception as e:
        print(f"Failed to process {sql_file}: {str(e)}")
