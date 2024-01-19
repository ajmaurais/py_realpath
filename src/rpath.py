
import sys
import os.path
import argparse
import subprocess

ARG_E_IGNORE = "ignore"
ARG_E_IGNORE_SKIP = "ignoreSkip"
ARG_E_WARN = "warn"
ARG_E_EXIT = "exit"
ARG_E_EXIT_SILENT = "exitSilent"


def copy_to_tmux_buffer(s, verbose=True):
    ''' Copy string to tmux buffer. '''

    if verbose:
        sys.stdout.write('Copying file paths to tmux terminal buffer...')

    tmux_command = ['tmux', 'set-buffer', s]
    r = subprocess.run(tmux_command, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if r.returncode != 0:
        sys.stderr.write('Failed to write to tmux buffer!')
        
        if verbose:
            std.stderr.write(r.stdout)


def main():
    parser = argparse.ArgumentParser(description = "Resolve relative file paths to absolute file path.")
    
    parser.add_argument("file", type = str, nargs = "+",
                        help = "file to get path of")

    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Write verbose output.')
    
    parser.add_argument("-e",
                        type = str,
                        choices = [ARG_E_IGNORE, ARG_E_IGNORE_SKIP, ARG_E_WARN, ARG_E_EXIT, ARG_E_EXIT_SILENT],
                        default = ARG_E_WARN)
    
    #read and check user suplied arguments
    args = parser.parse_args()
    
    paths = list()
    for fname in args.file:
        #get real path
        rpath = os.path.realpath(fname)
        #check that file exists
        fileExists = os.path.isfile(rpath) or os.path.isdir(rpath)
    
        paths.append(rpath)
        if fileExists:
            sys.stdout.write(f'{rpath}\n')
        else:
            if args.e == ARG_E_IGNORE_SKIP:
                continue
            elif args.e == ARG_E_IGNORE:
                sys.stdout.write(f'{rpath}\n')
            elif args.e == ARG_E_EXIT_SILENT:
                sys.exit(1)
            elif args.e == ARG_E_WARN or args.e == ARG_E_EXIT:
                sys.stdout.write(fname + " does not exist!\n")
                if args.e == ARG_E_WARN:
                    sys.stdout.write(f'{rpath}\n')
                elif args.e == ARG_E_EXIT:
                    sys.exit(1)
    
    paths = ' '.join(paths)
    copy_to_tmux_buffer(paths, args.verbose)


if __name__ == '__main__':
    main()

