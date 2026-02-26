
import os.path
import argparse
import sys
import shutil
import subprocess
import platform

ARG_E_IGNORE = "ignore"
ARG_E_IGNORE_SKIP = "ignoreSkip"
ARG_E_WARN = "warn"
ARG_E_EXIT = "exit"
ARG_E_EXIT_SILENT = "exitSilent"

# Helper for formatting file names for stdout/stderr
def _format_name(p: str, enquote: bool) -> str:
    return f'"{p}"' if enquote else p

# Copy text to system clipboard
def _to_clipboard(text: str) -> None:
    if platform.system() == "Darwin" and shutil.which("pbcopy"):
        try:
            subprocess.run(["pbcopy"], input=text.strip(), text=True, check=False)
        except Exception:
            pass
    elif platform.system() == "Linux" and os.environ.get("TMUX") and shutil.which("tmux"):
        try:
            subprocess.run(["tmux", "load-buffer", "-"], input=text.strip(), text=True, check=False)
        except Exception:
            pass

# Parse field separator like awk -F: accept any string and honor C-style escapes (e.g., \t, \n)
def _parse_field_separator(val: str) -> str:
    try:
        return bytes(val, "utf-8").decode("unicode_escape")
    except Exception:
        return val

def main():
    parser = argparse.ArgumentParser(description = "Resolve relative file paths to absolute file path.")

    parser.add_argument(
        "file", nargs = "+",
        help = "File(s) to get path of"
    )
    parser.add_argument(
        "-e",
        choices = [ARG_E_IGNORE, ARG_E_IGNORE_SKIP, ARG_E_WARN, ARG_E_EXIT, ARG_E_EXIT_SILENT],
        default = ARG_E_WARN,
        help='How to handle non-existing files: '
    )
    parser.add_argument(
        "-q", "--enquote", action="store_true",
        help="Surround printed resolved paths with quotes"
    )
    parser.add_argument(
        "-F", dest="fs", metavar="sep", default=" ",
        help="Output field separator"
    )
    parser = parser.parse_args()

    # Resolve field separator
    sep = _parse_field_separator(parser.fs)

    printed_any = False
    outputs = []

    for fname in parser.file:
        #get real path
        rpath = os.path.realpath(fname)
        #check that file exists
        fileExists = os.path.isfile(rpath) or os.path.isdir(rpath)

        if fileExists:
            out = _format_name(rpath, parser.enquote)
            if printed_any:
                print(sep, end="")
            print(out, end="")
            outputs.append(out)
            printed_any = True

        else:
            if parser.e == ARG_E_IGNORE_SKIP:
                continue

            elif parser.e == ARG_E_IGNORE:
                out = _format_name(rpath, parser.enquote)
                if printed_any:
                    print(sep, end="")
                print(out, end="")
                outputs.append(out)
                printed_any = True

            elif parser.e == ARG_E_EXIT_SILENT:
                if printed_any:
                    print()
                content = sep.join(outputs) + ("\n" if printed_any else "")
                _to_clipboard(content)
                exit()

            elif parser.e == ARG_E_WARN or parser.e == ARG_E_EXIT:
                print(_format_name(fname, parser.enquote) + " does not exist!", file=sys.stderr)
                if parser.e == ARG_E_WARN:
                    out = _format_name(rpath, parser.enquote)
                    if printed_any:
                        print(sep, end="")
                    print(out, end="")
                    outputs.append(out)
                    printed_any = True

                elif parser.e == ARG_E_EXIT:
                    if printed_any:
                        print()
                    content = sep.join(outputs) + ("\n" if printed_any else "")
                    _to_clipboard(content)
                    exit()

    if printed_any:
        print()
    content = sep.join(outputs) + ("\n" if printed_any else "")
    _to_clipboard(content)


if __name__ == '__main__':
    main()
