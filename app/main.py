import sys


def main():
    commands = {
        "builtin": "[echo, type, exit]",
        "executable": "",
    }
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
            if command in commands["builtin"]:
                print(f"{command} is a shell builtin")
                continue
        print(f"{command}: not found")


if __name__ == "__main__":
    main()
