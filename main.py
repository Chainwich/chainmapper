#!/usr/bin/env python3

from dotenv import dotenv_values


def main(cfg):
    pass


def dotconfig(path=".env"):
    return dotenv_values(path)


if __name__ == "__main__":
    main(dotconfig())
