import os
import shutil
import subprocess
import sys

commands = ["exit", "echo", "type", "pwd", "cd"]


def handle_redirection(args):
    output_file = args[args.index(">") + 1]
    input = runcommand(args[: args.index(">")])
    with open(output_file, "w") as f:
        f.write(input)
    return


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

    if current_token:
        args.append(current_token)

    return args


def handle_type(cmd):
    if cmd in commands:
        return f"{cmd} is a shell builtin"
    elif len(cmd) == 0:
        return ""
    elif path := shutil.which(cmd):
        return f"{cmd} is {path}"
    else:
        return f"{cmd}: not found"


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


def echo(args) -> str:
    txt = " ".join(args)
    return txt


def runcommand(args):
    if ">" in args or "<" in args:
        handle_redirection(args)

    match args[0]:
        case "exit":
            sys.exit(0)
        case "echo":
            return echo(args[1:])
        case "type":
            if len(args) == 1:
                return ""
            return handle_type(args[1])
        case "pwd":
            return os.getcwd()
        case "cd":
            cd(args[1:])

        case _:  # in case of non-built-in commands
            if path := shutil.which(args[0]):
                try:
                    args[0] = path
                    result = subprocess.run(
                        args, capture_output=True, text=True, check=True
                    )
                    command_output = result.stdout
                    return command_output.strip()

                except subprocess.CalledProcessError as e:
                    return f"Command failed with error: {e.stderr}"
            else:
                return f"{args[0]}: command not found"


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        args = generate_arguments(command)
        if ">" in args or "1>" in args:
            handle_redirection(args)
            continue
        else:
            output = runcommand(args)
            if output:
                print(output)


if __name__ == "__main__":
    main()
