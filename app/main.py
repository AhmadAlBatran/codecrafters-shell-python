import sys


def main():
    while True:
        if command != "exit":
            sys.stdout.write("$ ")
            command = input()
            print(f"{command}: command not found")
        else:
            break

    pass


if __name__ == "__main__":
    main()
