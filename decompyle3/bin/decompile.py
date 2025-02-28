#!/usr/bin/env python
# Mode: -*- python -*-
#
# Copyright (c) 2015-2017, 2019-2021 by Rocky Bernstein
# Copyright (c) 2000-2002 by hartmut Goebel <h.goebel@crazy-compilers.com>
#
import sys, os, getopt, time
from xdis.version_info import version_tuple_to_str

program = "decompyle3"

__doc__ = f"""
Usage:
  {program} [OPTIONS]... [ FILE | DIR]...
  {program} [--help | -h | --V | --version]

Examples:
  {program}      foo.pyc bar.pyc       # decompile foo.pyc, bar.pyc to stdout
  {program} -o . foo.pyc bar.pyc       # decompile to ./foo.pyc_dis and ./bar.pyc_dis
  {program} -o /tmp /usr/lib/python1.5 # decompile whole library

Options:
  -o <path>     output decompiled files to this path:
                if multiple input files are decompiled, the common prefix
                is stripped from these names and the remainder appended to
                <path>
                  decompyle3 -o /tmp bla/fasel.pyc bla/foo.pyc
                    -> /tmp/fasel.pyc_dis, /tmp/foo.pyc_dis
                  decompyle3 -o /tmp bla/fasel.pyc bar/foo.pyc
                    -> /tmp/bla/fasel.pyc_dis, /tmp/bar/foo.pyc_dis
                  decompyle3 -o /tmp /usr/lib/python1.5
                    -> /tmp/smtplib.pyc_dis ... /tmp/lib-tk/FixTk.pyc_dis
  --compile | -c <python-file>
                attempts a decompilation after compiling <python-file>
  -d            print timestamps
  -p <integer>  use <integer> number of processes
  -r            recurse directories looking for .pyc and .pyo files
  --fragments   use fragments deparser
  --verify-run  compile generated source, run it and check exit code
  --syntax-verify compile generated source
  --linemaps    generated line number correspondencies between byte-code
                and generated source output
  --encoding    <encoding>
                use <encoding> in generated source according to pep-0263
  --help        show this message

Debugging Options:
  --asm     | -a        include byte-code
  --grammar | -g        show matching grammar
  --tree={{before|after}}
  -t {{before|after}}     include syntax before (or after) tree transformation
  --tree++ | -T         add template rules to --tree=before when possible

Extensions of generated files:
  '.pyc_dis' '.pyo_dis'   successfully decompiled
    + '_unverified'       successfully decompile but verification failed
    + '_failed'           decompile failed (contact author for enhancement)
"""

program = "decompyle3"

from decompyle3.main import main, status_msg
from decompyle3.version import __version__


def usage():
    print(__doc__)
    sys.exit(1)


def main_bin():
    version_tuple = sys.version_info[0:2]
    if version_tuple < (3, 7):
        print(
            f"Error: {program} runs from Python 3.7 or greater."
            f""" \n\tYou have version: {version_tuple_to_str()}."""
        )
        sys.exit(-1)

    do_verify = recurse_dirs = False
    numproc = 0
    outfile = "-"
    out_base = None
    source_paths = []
    timestamp = False
    timestampfmt = "# %Y.%m.%d %H:%M:%S %Z"

    try:
        opts, pyc_paths = getopt.getopt(
            sys.argv[1:],
            "hac:gtTdrVo:p:",
            "help asm compile= grammar linemaps recurse "
            "timestamp tree= tree+ "
            "fragments verify verify-run version "
            "syntax-verify "
            "showgrammar".split(" "),
        )
    except getopt.GetoptError as e:
        print("%s: %s" % (os.path.basename(sys.argv[0]), e), file=sys.stderr)
        sys.exit(-1)

    options = {}
    for opt, val in opts:
        if opt in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif opt in ("-V", "--version"):
            print("%s %s" % (program, __version__))
            sys.exit(0)
        elif opt == "--syntax-verify":
            options["do_verify"] = "weak"
        elif opt == "--fragments":
            options["do_fragments"] = True
        elif opt == "--verify-run":
            options["do_verify"] = "verify-run"
        elif opt == "--linemaps":
            options["do_linemaps"] = True
        elif opt in ("--asm", "-a"):
            options["showasm"] = "after"
            options["do_verify"] = None
        elif opt in ("--tree", "-t"):
            if "showast" not in options:
                options["showast"] = {}
            if val == "before":
                options["showast"][val] = True
            elif val == "after":
                options["showast"][val] = True
            else:
                options["showast"]["before"] = True
            options["do_verify"] = None
        elif opt in ("--tree+", "-T"):
            if "showast" not in options:
                options["showast"] = {}
            options["showast"]["Full"] = True
            options["do_verify"] = None
        elif opt in ("--grammar", "-g"):
            options["showgrammar"] = True
        elif opt == "-o":
            outfile = val
        elif opt in ("--timestamp", "-d"):
            timestamp = True
        elif opt in ("--compile", "-c"):
            source_paths.append(val)
        elif opt == "-p":
            numproc = int(val)
        elif opt in ("--recurse", "-r"):
            recurse_dirs = True
        elif opt == "--encoding":
            options["source_encoding"] = val
        else:
            print(opt, file=sys.stderr)
            usage()

    # expand directory if specified
    if recurse_dirs:
        expanded_files = []
        for f in pyc_paths:
            if os.path.isdir(f):
                for root, _, dir_files in os.walk(f):
                    for df in dir_files:
                        if df.endswith(".pyc") or df.endswith(".pyo"):
                            expanded_files.append(os.path.join(root, df))
        pyc_paths = expanded_files

    # argl, commonprefix works on strings, not on path parts,
    # thus we must handle the case with files in 'some/classes'
    # and 'some/cmds'
    src_base = os.path.commonprefix(pyc_paths)
    if src_base[-1:] != os.sep:
        src_base = os.path.dirname(src_base)
    if src_base:
        sb_len = len(os.path.join(src_base, ""))
        pyc_paths = [f[sb_len:] for f in pyc_paths]

    if not pyc_paths and not source_paths:
        print("No input files given to decompile", file=sys.stderr)
        usage()

    if outfile == "-":
        outfile = None  # use stdout
    elif outfile and os.path.isdir(outfile):
        out_base = outfile
        outfile = None
    elif outfile and len(pyc_paths) > 1:
        out_base = outfile
        outfile = None

    if timestamp:
        print(time.strftime(timestampfmt))

    if numproc <= 1:
        try:
            result = main(
                src_base, out_base, pyc_paths, source_paths, outfile, **options
            )
            result = list(result) + [options.get("do_verify", None)]
            if len(pyc_paths) > 1:
                mess = status_msg(do_verify, *result)
                print("# " + mess)
                pass
        except ImportError as e:
            print(str(e))
            sys.exit(2)
        except (KeyboardInterrupt):
            pass
    else:
        from multiprocessing import Process, Queue

        try:
            from Queue import Empty
        except ImportError:
            from queue import Empty

        fqueue = Queue(len(pyc_paths) + numproc)
        for f in pyc_paths:
            fqueue.put(f)
        for i in range(numproc):
            fqueue.put(None)

        rqueue = Queue(numproc)

        def process_func():
            try:
                (tot_files, okay_files, failed_files, verify_failed_files) = (
                    0,
                    0,
                    0,
                    0,
                )
                while 1:
                    f = fqueue.get()
                    if f is None:
                        break
                    (t, o, f, v) = main(
                        src_base, out_base, [f], None, outfile, **options
                    )
                    tot_files += t
                    okay_files += o
                    failed_files += f
                    verify_failed_files += v
            except (Empty, KeyboardInterrupt):
                pass
            rqueue.put((tot_files, okay_files, failed_files, verify_failed_files))
            rqueue.close()

        try:
            procs = [Process(target=process_func) for i in range(numproc)]
            for p in procs:
                p.start()
            for p in procs:
                p.join()
            try:
                (tot_files, okay_files, failed_files, verify_failed_files) = (
                    0,
                    0,
                    0,
                    0,
                )
                while True:
                    (t, o, f, v) = rqueue.get(False)
                    tot_files += t
                    okay_files += o
                    failed_files += f
                    verify_failed_files += v
            except Empty:
                pass
            print(
                "# decompiled %i files: %i okay, %i failed, %i verify failed"
                % (tot_files, okay_files, failed_files, verify_failed_files)
            )
        except (KeyboardInterrupt, OSError):
            pass

    if timestamp:
        print(time.strftime(timestampfmt))

    return


if __name__ == "__main__":
    main_bin()
