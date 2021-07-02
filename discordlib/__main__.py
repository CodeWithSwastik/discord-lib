from sys import argv
from .client import Client

def main():
    if len(argv) <= 1:
        print("Please enter a file to run!")
    else:
        fp = argv[1]
        bot = Client(fp)
        bot.run()

if __name__ == '__main__':
    main()