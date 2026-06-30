import os
import sys

path = os.environ.get("PATH")


def commandtype(command, builtin, path):

    if command in builtin:
        return "builtin"
    else:
        pass


def main():
    builtin = ["echo", "type", "exit"]

    while True:
        sys.stdout.write("$ ")
        command = input()

        if command == "exit":
            break
        if command.startswith("echo"):
            print(command[5:])
            continue
        if command.startswith("type"):
            command = command[5:]
            if command in builtin:
                print(f"{command} is a shell builtin")
                continue
        print(f"{command}: not found")


if __name__ == "__main__":
    main()
