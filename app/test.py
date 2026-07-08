import os
import shutil
import sys
from dataclasses import dataclass, field

commands = ["exit", "echo", "type", "pwd", "cd"]


def generate_arguments(command):
    args = []
    current_token = ""
    in_single_quote = False
    in_double_quote = False
    skip = False

    for i in range(len(command)):
        char = command[i]

        if skip:
            skip = False
            current_token += char
            continue

        elif char == "\\" and not in_single_quote:
            skip = True
            continue
        elif char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == " " and not in_single_quote and not in_double_quote:
            if current_token:
                args.append(current_token)
                current_token = ""
        else:
            current_token += char


class Shell:
    def __init__(self):

        pass

    def run(self):
        while True:
            sys.stdout.write("$ ")
            command = input()
            if command == "exit":
                break


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == "exit":
            break


if __name__ == "__main__":
    main()
