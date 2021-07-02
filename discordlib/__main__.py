from argparse import ArgumentParser
from pathlib import Path

from .client import Client

def main():
    parser = ArgumentParser("discord-lib")
    parser.add_argument("filename", type=Path)
    args = parser.parse_args()
    fp = args.filename
    bot = Client(str(fp))
    bot.run()

if __name__ == '__main__':
    main()
