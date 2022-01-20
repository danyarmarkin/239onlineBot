from sqlite3 import *


class UsersTable:
    path = "database.sqlite"
    columns = "(id integer, name text, surname text)"

    def create(self):
        connection = connect(self.path)
        cursor = connection.cursor()
        cursor.execute(f"CREATE TABLE users {self.columns}")
        connection.commit()
        connection.close()

    def exists(self):
        connection = connect(self.path)
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        res = cursor.fetchall()
        connection.commit()
        connection.close()
        return "users" in [i[0] for i in res]

    def add(self, user_id: int, name: str, surname: str):
        connection = connect(self.path)
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
        cursor.execute(f"INSERT INTO users VALUES {(user_id, name, surname)}")
        connection.commit()
        connection.close()

    def getLinesFromTable(self, table="users", orderby="surname"):
        connection = connect(self.path)
        cursor = connection.cursor()
        lines = list(cursor.execute(f"SELECT * FROM {table} ORDER BY {orderby}"))
        connection.commit()
        connection.close()
        return lines

    def getUser(self, user_id):
        lines = self.getLinesFromTable("users", "surname")
        for line in lines:
            if line[0] == user_id:
                return line[2], line[1]
        return "No", "Name"

    def haveUser(self, user_id):
        lines = self.getLinesFromTable("users", "surname")
        for line in lines:
            if line[0] == user_id:
                return True
        return False
