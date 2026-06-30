import sys


def main():
    sys.stdout.write("$ ")
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == "exit":
            break
        print(f"{command}: command not found")

    pass


if __name__ == "__main__":
    main()
