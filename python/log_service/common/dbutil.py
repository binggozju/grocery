#!/usr/bin/python
"""
database utility
"""

import MySQLdb

database = {
        "host": "",
        "port": 3306,
        "db": "",
        "user": "",
        "password": "",
        "charset": "utf8"
    }

def init(host, db, user, password, port=3306, charset="utf8"):
    global database
    database["host"] = host
    database["port"] = port
    database["db"] = db
    database["user"] = user
    database["password"] = password
    database["charset"] = charset
    print "init the dbutil module successfully"

class DBUtil():
    """
    utility for accessing database
    """
    def __init__(self):
        self.conn = MySQLdb.connect(host=database["host"], port=database["port"], db=database["db"], user=database["user"], passwd=database["password"], charset=database["charset"])
        print "create a database connection: host -> %s, db -> %s" % (database["host"], database["db"])

    def __del__(self):
        self.conn.close()
        print "close the database connection to mysql"

    def close(self):
        self.conn.close()
        print "close the database connection to mysql"

    def query(self, sql):
        """used for select operation"""
        result = {}
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
        except Exception as e:
            print "error, fail to execute %s: %s" % (sql, e)
            cur.close()
        return result

    def execute(self, sql):
        """used for insert operation"""
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
        except Exception as e:
            print "error, fail to %s: %s" % (sql, e)
            cur.close()
            self.conn.close()
            self.conn = MySQLdb.connect(host=database["host"], port=database["port"], db=database["db"], user=database["user"], passwd=database["password"], charset=database["charset"])
            print "reconnect to mysql"
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()

    def execute_batch(self, sql, args):
        """
        insert multiple sets of data in batch
        @sql, an sql sentence with parameters
        @args, a list of data tuples
        """
        try:
            cur = self.conn.cursor()
            cur.executemany(sql, args)
            self.conn.commit()
        except Exception as e:
            print "error, execute_batch %s failed: %s" % (sql, e)
        finally:
            cur.close()


if __name__ == "__main__":
    init("localhost", "testdb", "root", "123456")
    db_util = DBUtil()

    sql_insert = "insert into friends(name, age, home, update_time) values(\"binggo\", 27, \"hubei\", now())"
    db_util.execute(sql_insert)

    sql_select = "select * from friends"
    result = db_util.query(sql_select)
    print result

    del db_util
