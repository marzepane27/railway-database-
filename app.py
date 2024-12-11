import psycopg2
from psycopg2 import sql

host = 'junction.proxy.rlwy.net'
port = '19910'  
database = 'RailwayDB'  
user = 'postgres'  
password = 'ybFsTxMPmeikkNgpBcAGDwjbLfMGJbDG'  

try:
    connection = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    cursor = connection.cursor()

    cursor.execute("SELECT to_regclass('public.users');")
    table_exists = cursor.fetchone()[0]

    if table_exists:
        print("Таблица 'users' уже существует.")
    else:
        print("Таблица 'users' не найдена. Создаю таблицу...")
        create_table_query = '''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            name VARCHAR(100),
            age INT,
            email VARCHAR(100),
            phone VARCHAR(15),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("Таблица успешно создана!")

    cursor.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'users';
    """)

    columns = [column[0] for column in cursor.fetchall()]
    required_columns = {
        'name': "ALTER TABLE users ADD COLUMN name VARCHAR(100);",
        'age': "ALTER TABLE users ADD COLUMN age INT;",
        'username': "ALTER TABLE users ADD COLUMN username VARCHAR(100) NOT NULL;",
        'email': "ALTER TABLE users ADD COLUMN email VARCHAR(100);",
        'phone': "ALTER TABLE users ADD COLUMN phone VARCHAR(15);",
        'address': "ALTER TABLE users ADD COLUMN address TEXT;"
    }

    for col, query in required_columns.items():
        if col not in columns:
            cursor.execute(query)
            print(f"Столбец '{col}' добавлен.")

    connection.commit()

    def add_user(username, name, age, email, phone, address):
        insert_query = '''
        INSERT INTO users (username, name, age, email, phone, address) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING;
        '''
        cursor.execute(insert_query, (username, name, age, email, phone, address))
        connection.commit()
        print(f"Пользователь {username} добавлен.")

    users_to_add = [
        ('jane_smith', 'Jane Smith', 30, 'jane.smith@example.com', '123-456-7890', '123 Elm Street'),
        ('john_doe', 'John Doe', 25, 'john.doe@example.com', '987-654-3210', '456 Oak Avenue'),
        ('alice_brown', 'Alice Brown', 28, 'alice.brown@example.com', '555-789-1234', '789 Pine Road')
    ]

    for user in users_to_add:
        add_user(*user)

    def update_user(username, **kwargs):
        update_clauses = []
        params = []
        for key, value in kwargs.items():
            update_clauses.append(f"{key} = %s")
            params.append(value)
        params.append(username)
        update_query = f"UPDATE users SET {', '.join(update_clauses)} WHERE username = %s;"
        cursor.execute(update_query, params)
        connection.commit()
        print(f"Пользователь {username} обновлен.")

    update_user('jane_smith', age=31, phone='123-456-0000')

    def delete_user(username):
        delete_query = "DELETE FROM users WHERE username = %s;"
        cursor.execute(delete_query, (username,))
        connection.commit()
        print(f"Пользователь {username} удален.")

    delete_user('alice_brown')

    cursor.execute("SELECT * FROM users;")
    rows = cursor.fetchall()
    print("Данные из таблицы 'users':")
    for row in rows:
        print(row)

except Exception as error:
    print(f"Ошибка при работе с базой данных: {error}")

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
