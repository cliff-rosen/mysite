
LOG_FILE_NAME = 'log.txt'
DELIMETER = "---------------------------------------------------\n"

class Logger:
    def __init__(self, filename = LOG_FILE_NAME):
        if filename:
            self.filename = filename
        else:
            self.filename = LOG_FILE_NAME
        print("Logger created, using", self.filename)

    def log(self, msg):
        try:
            with open(self.filename, "a", encoding='utf-8') as file:
                file.writelines(DELIMETER + msg + "\n\n")
        except Exception as e:
            print("LOG ERROR")
            print(e)

