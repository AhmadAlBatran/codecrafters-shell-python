import os
import shutil
import sys

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

        elif char == "\\":
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

    if current_token:
        args.append(current_token)

    return args


def handle_type(cmd):
    if cmd in commands:
        print(f"{cmd} is a shell builtin")
    elif path := shutil.which(cmd):
        print(f"{cmd} is {path}")
    else:
        print(f"{cmd}: not found")


def cd(args):
    if len(args) == 0:
        os.chdir(os.path.expanduser("~"))
    elif args[0] == "~":
        os.chdir(os.path.expanduser("~"))
    else:
        try:
            os.chdir(args[0])
        except FileNotFoundError:
            print(f"{args[0]}: No such file or directory")


def runcommand(args):
    args = generate_arguments(" ".join(args))

    match args[0]:
        case "exit":
            sys.exit(0)
        case "echo":
            txt = " ".join(args[1:])
            print(txt)
        case "type":
            handle_type(args[1])
        case "pwd":
            print(os.getcwd())
        case "cd":
            cd(args[1:])
        case _:  # incase of not built in commands scan path untill you find it
            if path := shutil.which(args[0]):
                pid = os.fork()
                if pid == 0:
                    os.execvp(args[0], args)
                else:
                    os.waitpid(pid, 0)
            else:
                print(f"{args[0]}: command not found")


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()

        arguments = command.split(" ")
        runcommand(arguments)


if __name__ == "__main__":
    main()
