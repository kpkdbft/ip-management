import sqlite3
import requests
import json

headers = {"Content-Type": "application/json"}
ipManagementUrl = "http://localhost:8080/api/zabbix"


def main():
    dbname = "ip_management.db"
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.execute("select * from sqlite_master where type='table'")
    tables = cur.fetchall()
    if (len(tables)) != 2:
        print("先にapp.pyを実行してください")
        return

    admins = [
        {"name": "taro", "grade": "M2"},
        {"name": "hanako", "grade": "M1"},
        {"name": "jiro", "grade": "B4"},
    ]
    for i, admin in enumerate(admins):
        cur.execute(
            f'INSERT INTO admin values({i}, "{admin["name"]}", "{admin["grade"]}")'
        )
    conn.commit()
    cur.close()
    conn.close()

    ipLists = ["192.168.1.1", "192.168.1.43", "192.168.1.33"]
    r = requests.post(
        ipManagementUrl, data=json.dumps({"ping": ipLists}), headers=headers
    )

    ipLists = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
    r = requests.post(
        ipManagementUrl, data=json.dumps({"ping": ipLists}), headers=headers
    )
    print(r.status_code)


if __name__ == "__main__":
    main()
