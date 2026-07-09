import os
import shutil
import subprocess
import sys

commands = ["exit", "echo", "type", "pwd", "cd"]


def handle_redirection(args):
    redirect_operators = [">", "1>"]
    op = next((o for o in redirect_operators if o in args), None)

    if op is None:
        return "No redirection found"

    ind = args.index(op)
    output_file = args[ind + 1]
    result = runcommand(args[:ind])

    if not result["success"]:
        print(result["output"], file=sys.stderr)
        return

    with open(output_file, "w") as f:
        f.write(result["output"])


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
    match args[0]:
        case "exit":
            sys.exit(0)
        case "echo":
            return {"success": True, "output": echo(args[1:])}
        case "type":
            if len(args) == 1:
                return {"success": True, "output": ""}
            return {"success": True, "output": handle_type(args[1])}
        case "pwd":
            return {"success": True, "output": os.getcwd()}
        case "cd":
            cd(args[1:])
            return {"success": True, "output": ""}
        case _:  # in case of non-built-in commands
            if path := shutil.which(args[0]):
                try:
                    args[0] = path
                    result = subprocess.run(
                        args, capture_output=True, text=True, check=True
                    )
                    return {"success": True, "output": result.stdout.strip()}
                except subprocess.CalledProcessError as e:
                    return {"success": False, "output": e.stderr}
            else:
                return {"success": False, "output": f"{args[0]}: command not found"}


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        args = generate_arguments(command)
        if ">" in args or "1>" in args:
            handle_redirection(args)
            continue
        result = runcommand(args)
        if result["success"]:
            print(result["output"].strip())
        else:
            print(result["output"].strip())


if __name__ == "__main__":
    main()
