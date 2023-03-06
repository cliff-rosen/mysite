from datetime import datetime

LOG_FILE_NAME = 'log.txt'
DELIMETER = "---------------------------------------------------\n"

class Logger:
    def __init__(self, filename = LOG_FILE_NAME):
        if filename:
            self.filename = filename
        else:
            self.filename = LOG_FILE_NAME
        print("Logger created, using", self.filename)
        try:
            with open(self.filename, "w", encoding='utf-8') as file:
                file.writelines(self.get_timestamp() + ': logger started' + "\n\n")
        except Exception as e:
            print("LOG ERROR")
            print(e)


    def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]


    def write_log(self, level, msg):
        try:
            with open(self.filename, "a", encoding='utf-8') as file:
                file.writelines(self.get_timestamp() + f' ({level}): ' + msg + "\n\n")
        except Exception as e:
            print("LOG ERROR")
            print(e)


    def log(self, msg):
        self.write_log('LEGACY', msg)


    def debug(self, msg):
        print('DEBUG: ' + msg)
        self.write_log('DEBUG', msg)
