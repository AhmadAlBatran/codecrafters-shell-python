import sys


def main():
    while True:
        sys.stderr.write("$ ")
        command = input()
        if command != "exit":
            print(f"{command}: command not found")
            sys.stdout.write("$ ")
            command = input()
        elif command == "exit":
            break

    pass


if __name__ == "__main__":
    main()
