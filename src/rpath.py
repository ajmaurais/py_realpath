
import os.path
import argparse

ARG_E_IGNORE = "ignore"
ARG_E_IGNORE_SKIP = "ignoreSkip"
ARG_E_WARN = "warn"
ARG_E_EXIT = "exit"
ARG_E_EXIT_SILENT = "exitSilent"

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

    #read and check user suplied arguments
    parser = parser.parse_args()

    for fname in parser.file:
        #get real path
        rpath = os.path.realpath(fname)
        #check that file exists
        fileExists = os.path.isfile(rpath) or os.path.isdir(rpath)

        if fileExists:
            print(rpath)
        else:
            if parser.e == ARG_E_IGNORE_SKIP:
                continue
            elif parser.e == ARG_E_IGNORE:
                print(rpath)
            elif parser.e == ARG_E_EXIT_SILENT:
                exit()
            elif parser.e == ARG_E_WARN or parser.e == ARG_E_EXIT:
                print(fname + " does not exist!")
                if parser.e == ARG_E_WARN:
                    print(rpath)
                elif parser.e == ARG_E_EXIT:
                    exit()

if __name__ == '__main__':
    main()
