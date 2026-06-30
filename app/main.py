import os
import shutil
import sys

commands = ["exit", "echo", "type"]


def handle_type(cmd):
    if cmd in commands:
        print(f"{cmd} is a shell builtin")
    elif path := shutil.which(cmd):
        print(f"{cmd} is {path}")
    else:
        print(f"{cmd}: not found")


def handle_builtin(args):
    match args[0]:
        case "exit":
            sys.exit(0)
        case "echo":
            txt = " ".join(args[1:])
            print(txt)
        case "type":
            handle_type(args[1])
        case _:
            print(f"{args[0]}: command not found")


def main():
    while True:
        sys.stdout.write("$ ")
        command = input("")
        arguments = command.split(" ")
        handle_builtin(arguments)


if __name__ == "__main__":
    main()
