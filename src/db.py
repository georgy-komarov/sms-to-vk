import json
import subprocess
import csv
import pipes


class DBHelper:
    def __init__(self, path='/data/user_de/0/com.android.providers.telephony/databases/mmssms.db'):
        self.path = path

    def query(self, query):
        cmd = f'sqlite3 -csv -header {self.path} {pipes.quote(query)}'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        sqlite_out, sqlite_stderr = p.communicate()
        reader = csv.DictReader(sqlite_out.split("\n"))
        return list(reader)

    def read_all_messages(self):
        self.query('UPDATE sms SET read = 1')

    def get_unread_messages(self):
        messages = self.query('SELECT * FROM sms WHERE read = 0')
        return messages

    def get_last_messages(self, count: int):
        return self.query(f'SELECT * FROM (SELECT * FROM sms ORDER BY _id DESC LIMIT {count}) Var1 ORDER BY _id')


if __name__ == '__main__':
    sms = DBHelper('../examples/mmssms.db')
    json.dump(sms.get_unread_messages(), open('../examples/sms.json', 'w'), ensure_ascii=False, indent=2)
