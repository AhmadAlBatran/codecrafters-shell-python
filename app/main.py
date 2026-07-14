import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
import readline


commands = ["exit", "echo", "type", "pwd", "cd"]
redirect_operators = [">", "1>", "2>",">>","1>>","2>>"]


@dataclass
class CommandResult:
    success: bool
    return_code: int
    stdout: str = ""
    stderr: str = ""

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
                return CommandResult(success=False,return_code=127,stderr=f"{args[0]}: command not found",)


def handle_redirection(args):
    op = next((o for o in redirect_operators if o in args), None)
    if op is None:
        return runcommand(args)  # no redirection, just run normally

    ind = args.index(op)
    if ind + 1 >= len(args):
        return CommandResult(
            success=False,
            return_code=1,
            stderr=f"shell: syntax error near unexpected token `{op}'\n",
        )

    output_file = args[ind + 1]
    result = runcommand(args[:ind])

    match op:
        case ">" | "1>":
            content = result.stdout
            mode = "w"
        case ">>" | "1>>":
            content = result.stdout
            mode = "a"
        case "2>":
            content = result.stderr
            mode = "w"
        case "2>>":
            content = result.stderr
            mode = "a"
        case "&>" | ">&":
            content = result.stdout + result.stderr
            mode = "w"
        case _:
            content = result.stdout
            mode = "w"


    if content and not content.endswith("\n"):
        content += "\n"

    try:
        with open(output_file, mode) as f:
            f.write(content)
    except Exception as e:
        file_error = f"shell: {output_file}: {str(e)}\n"
        result.stderr += file_error
        result.success = False
        result.return_code = 1

    STDOUT_OPS = (">", ">>", "1>", "1>>", "&>", ">&")
    STDERR_OPS = ("2>", "2>>", "&>", ">&")

    return CommandResult(
        success=result.success,
        return_code=result.return_code,
        stdout="" if op in STDOUT_OPS else result.stdout,
        stderr="" if op in STDERR_OPS else result.stderr,
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

def completer(text, state):
    matches = [cmd for cmd in commands if cmd.startswith(text)]
    matches += [
        f for d in os.environ.get("PATH", "").split(os.pathsep)
        if os.path.isdir(d)
        for f in os.listdir(d)
        if f.startswith(text) and os.access(os.path.join(d, f), os.X_OK)
    ]
    matches = sorted(set(matches))
    try:
        return matches[state] + " "
    except IndexError:
        return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

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

        result = handle_redirection(args)
        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        continue

        result = runcommand(args)

        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)


if __name__ == "__main__":
    main()
