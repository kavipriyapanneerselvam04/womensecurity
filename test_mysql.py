import mysql.connector

passwords = ['ROOT', 'root', '', 'password', '123456', 'admin']

for pwd in passwords:
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=pwd,
            port=3306
        )
        print(f"✓ SUCCESS! Password is: '{pwd}'")
        conn.close()
        break
    except mysql.connector.Error as e:
        print(f"✗ Failed with password '{pwd}': {e.msg}")
