
import os
import argparse
import sys
import subprocess

ARG_E_IGNORE = "ignore"
ARG_E_IGNORE_SKIP = "ignoreSkip"
ARG_E_WARN = "warn"
ARG_E_EXIT = "exit"
ARG_E_EXIT_SILENT = "exitSilent"
ARG_C_DEFAULT = 1

def write_to_clipboard(output):
    process = subprocess.Popen('pbcopy',
                               env={'LANG': 'en_US.UTF-8'},
                               stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))

def printPath(path, copy_to_cb):
    sys.stdout.write(f'{path}\n')
    if copy_to_cb:
        write_to_clipboard(path)

def main():
    parser = argparse.ArgumentParser(description="Resolve relative file paths to absolute file path.")

    parser.add_argument("file", type=str, help="file to get path of", nargs="+")

    parser.add_argument("-e", type=str, default=ARG_E_WARN,
                        choices=[ARG_E_IGNORE, ARG_E_IGNORE_SKIP, ARG_E_WARN, ARG_E_EXIT, ARG_E_EXIT_SILENT],
                        help=f"Choose how to deal with files which do not exist {ARG_E_WARN} is the default")

    parser.add_argument('-c', choices=[0,1], default=ARG_C_DEFAULT, dest='copy_to_cb',
                        help=f'Choose whether to copy path to clipboard. Default is {ARG_C_DEFAULT}')

    # read and check user suplied arguments
    args = parser.parse_args()

    for fname in args.file:
        # get real path
        rpath = os.path.realpath(fname)

        # check that file exists
        fileExists = os.path.isfile(rpath) or os.path.isdir(rpath)

        if fileExists:
            printPath(rpath, args.copy_to_cb)
        else:
            if args.e == ARG_E_IGNORE_SKIP:
                continue
            elif args.e == ARG_E_IGNORE:
                printPath(rpath, args.copy_to_cb)
            elif args.e == ARG_E_EXIT_SILENT:
                sys.exit(0)
            elif args.e in (ARG_E_WARN, ARG_E_EXIT):
                print(fname + " does not exist!")
                if args.e == ARG_E_WARN:
                    printPath(rpath, args.copy_to_cb)
                elif args.e == ARG_E_EXIT:
                    sys.exit(1)

if __name__ == "__main__":
    main()

