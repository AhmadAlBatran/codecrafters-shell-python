import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

commands = ["exit", "echo", "type", "pwd", "cd"]
redirect_operators = [">", "1>"]


@dataclass
class CommandResult:
    success: bool
    return_code: int
    stdout: str = ""
    stderr: str = ""


def handle_redirection(args):
    op = next((o for o in redirect_operators if o in args), None)
    if op is None:
        return CommandResult(success=True, return_code=0)

    ind = args.index(op)
    output_file = args[ind + 1]
    result = runcommand(args[:ind])

    try:
        with open(output_file, "w") as f:
            f.write(result.stdout)
    except Exception as e:
        file_error = f"shell: {output_file}: {str(e)}\n"
        result.stderr += file_error
        result.success = False
        result.return_code = 1

    return CommandResult(
        success=result.success,
        return_code=result.return_code,
        stdout="",
        stderr=result.stderr,
    )


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
        return CommandResult(
            success=True, return_code=0, stdout=f"{cmd} is a shell builtin"
        )
    elif len(cmd) == 0:
        return CommandResult(success=True, return_code=0, stdout="")
    elif path := shutil.which(cmd):
        return CommandResult(success=True, return_code=0, stdout=f"{cmd} is {path}")
    else:
        return CommandResult(success=False, return_code=1, stderr=f"{cmd}: not found")


def cd(args):
    target_dir = (
        os.path.expanduser("~") if len(args) == 0 or args[0] == "~" else args[0]
    )
    try:
        os.chdir(target_dir)
        return CommandResult(success=True, return_code=0)
    except FileNotFoundError:
        return CommandResult(
            success=False,
            return_code=1,
            stderr=f"cd: {target_dir}: No such file or directory",
        )
    except PermissionError:
        return CommandResult(
            success=False,
            return_code=126,
            stderr=f"cd: {target_dir}: Permission denied",
        )


def runcommand(args):
    if not args:
        return CommandResult(success=True, return_code=0)

    match args[0]:
        case "exit":
            sys.exit(0)

        case "echo":
            txt = " ".join(args[1:])
            return CommandResult(success=True, return_code=0, stdout=txt)

        case "type":
            if len(args) == 1:
                return CommandResult(success=True, return_code=0, stdout="")
            return handle_type(args[1])

        case "pwd":
            return CommandResult(success=True, return_code=0, stdout=os.getcwd())

        case "cd":
            return cd(args[1:])

        case _:  # External commands
            if path := shutil.which(args[0]):
                try:
                    res = subprocess.run(
                        args, capture_output=True, text=True, check=False
                    )
                    return CommandResult(
                        success=(res.returncode == 0),
                        return_code=res.returncode,
                        stdout=res.stdout,
                        stderr=res.stderr,
                    )
                except Exception as e:
                    return CommandResult(success=False, return_code=1, stderr=str(e))
            else:
                return CommandResult(
                    success=False,
                    return_code=127,
                    stderr=f"{args[0]}: command not found",
                )


def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            command = input()
        except EOFError:
            print()
            break

        args = generate_arguments(command)
        if not args:
            continue

        if ">" in args or "1>" in args:
            handle_redirection(args)
            continue

        result = runcommand(args)

        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)


if __name__ == "__main__":
    main()
