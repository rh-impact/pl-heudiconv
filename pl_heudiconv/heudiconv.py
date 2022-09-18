#
# heudiconv ds ChRIS plugin app
#
# (c) 2022 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import os
import subprocess

from chrisapp.base import ChrisApp


Gstr_title = r"""
 _                    _ _
| |                  | (_)
| |__   ___ _   _  __| |_  ___ ___  _ ____   __
| '_ \ / _ \ | | |/ _` | |/ __/ _ \| '_ \ \ / /
| | | |  __/ |_| | (_| | | (_| (_) | | | \ V /
|_| |_|\___|\__,_|\__,_|_|\___\___/|_| |_|\_/


"""

Gstr_synopsis = """

    NAME

       pl-heudiconv

    SYNOPSIS

        docker run --rm rh-impact/pl-heudiconv pl-heudiconv             \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir>

    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                             \\
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \\
                quay.io/rh-impact/pl-heudiconv pl-heudiconv         \\
                /incoming /outgoing

    DESCRIPTION

        `heudiconv` ...

    ARGS

        [-h] [--help]
        If specified, show help message and exit.

        [--json]
        If specified, show json representation of app and exit.

        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.

        [--savejson <DIR>]
        If specified, save json representation file to DIR and exit.

        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.

        [--version]
        If specified, print version number and exit.
"""


class Heudiconv(ChrisApp):
    """
    An app to organize brain imaging data into structured directory layouts.
    """
    PACKAGE                 = __package__
    TITLE                   = 'A ChRIS plugin for heudiconv'
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 2000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 8000  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """

        self.add_argument(
            '--inputdir-type',
            default='files',
            choices=('files', 'dicom_dir_template'),
            optional=True,
            dest='inputdir_type',
            type=str,
            help='''For input, heudiconv accepts EITHER a "--files"
            argument, or a "--dicom_dir_template" argument. This
            option specifies which to use for the positional
            "inputdir" argument to this plugin.''')

        self.add_argument(
            '-f', '--heuristic',
            optional=True,
            default='reproin',
            dest='heuristic',
            type=str,
            help='''Name of a known heuristic or path to the Python
            script containing heuristic.''')

        self.add_argument(
            '-b', '--bids',
            optional=True,
            default=False,
            dest='bids',
            type=bool,
            help='''Flag for output into BIDS structure. Can also take
            BIDS-specific options by using --bids-options, e.g.,
            --bids-options notop.''')

        self.add_argument(
            '--bids-options',
            optional=True,
            nargs='+',
            default=[],
            choices=['notop'],
            metavar=('BIDSOPTION1', 'BIDSOPTION2'),
            dest='bids_options',
            type=str,
            help='''The only currently supported bids options is
             "notop", which skips creation of top-level BIDS
             files. This is useful when running in batch mode to
             prevent possible race conditions.''')

        self.add_argument(
            '--overwrite',
            optional=True,
            default=False,
            dest='overwrite',
            type=bool,
            help='Overwrite existing converted files.')

        self.add_argument(
            '--datalad',
            optional=True,
            default=False,
            dest='datalad',
            type=bool,
            help='''Store the entire collection as DataLad
            dataset(s). Small files will be committed directly to git,
            while large to annex. New version (6) of annex
            repositories will be used in a "thin" mode so it would
            look to mortals as just any other regular directory
            (i.e. no symlinks to under .git/annex). For now just for
            BIDS mode.''')

        self.add_argument(
            '--minmeta',
            optional=True,
            default=False,
            dest='minmeta',
            type=bool,
            help='Exclude dcmstack meta information in sidecar jsons.')

        self.add_argument(
            '--random-seed',
            optional=True,
            default=[],
            dest='random_seed',
            type=int,
            help='Random seed to initialize RNG.')

        self.add_argument(
            '-l', '--locator',
            optional=True,
            default=[],
            dest='locator',
            type=str,
            help='''Study path under outdir. If provided, it overloads
            the value provided by the heuristic. If --datalad is
            enabled, every directory within locator becomes a
            super-dataset thus establishing a hierarchy. Setting to
            "unknown" will skip that dataset.''')

        self.add_argument(
            '-ss', '--ses',
            optional=True,
            default=[],
            dest='session',
            type=str,
            help='''Session for longitudinal study_sessions. Default is
            None.''')

        self.add_argument(
            '-p', '--with-prov',
            optional=True,
            default=False,
            dest='with_prov',
            type=bool,
            help='Store additional provenance information.')

        self.add_argument(
            '--command',
            default=[],
            choices=(
                'heuristics', 'heuristic-info', 'ls', 'populate-templates',
                'sanitize-jsons', 'treat-jsons', 'populate-intended-for'),
            optional=True,
            dest='command',
            type=str,
            help='''Custom action to be performed on provided files
            instead of regular operation.''')

        self.add_argument(
            '--anon-cmd',
            default=[],
            optional=True,
            dest='anon_cmd',
            type=str,
            help='Command to run to convert subject IDs used for DICOMs to '
            'anonymized IDs. Such command must take a single argument and '
            'return a single anonymized ID.')

        self.add_argument(
            '-s', '--subjects',
            dest='subjects',
            optional=True,
            default=[],
            type=str,
            nargs='*',
            help='''List of subjects - required for dicom template. If
            not provided, DICOMS would first be "sorted" and subject
            IDs deduced by the heuristic.''')

        self.add_argument(
            '-g', '--grouping',
            default=[],
            choices=('studyUID', 'accession_number', 'all', 'custom'),
            optional=True,
            dest='grouping',
            type=str,
            help='How to group dicoms (default: by studyUID)')

        self.add_argument(
            '--dcmconfig',
            default=[],
            optional=True,
            dest='dcmconfig',
            type=str,
            help='JSON file for additional dcm2niix configuration.')

        submission = self.add_argument_group('Conversion submission options')
        submission.add_argument(
            '-q', '--queue',
            choices=("SLURM", None),
            default=None,
            help='Batch system to submit jobs in parallel.')

        submission.add_argument(
            '--queue-args',
            dest='queue_args',
            default=None,
            help='''Additional queue arguments passed as a single
            string of space-separated Argument=Value pairs.''')

        gitopts = self.add_argument_group(
            'Git config arguments',
            'Used to set user details for git commits when using the datalad option.')

        gitopts.add_argument(
            '--git-user-name',
            default='ChRIS HeuDiConv Plugin',
            dest='git_user_name',
            type=str,
            help='''User name to use for Git commits when --datalad is
            specified. It will be set as the value of the
            "GIT_AUTHOR_NAME" and "GIT_COMMITTER_NAME" environment
            variables. Defaults to "ChRIS HeuDiConv Plugin"''')

        gitopts.add_argument(
            '--git-user-email',
            default='pl-heudiconv@chrisproject.org',
            dest='git_user_email',
            type=str,
            help='''User email to use for Git commits when --datalad
            is specified. It will be set as the value of the
            "GIT_AUTHOR_EMAIL" and "GIT_COMMITTER_EMAIL" environment
            variables. Defaults to "pl-heudiconv@chrisproject.org"''')

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """

        cmd = [
            'heudiconv',
            '--' + options.inputdir_type, options.inputdir,
            '--outdir', options.outputdir,
            '--heuristic', options.heuristic
        ]

        if options.bids:
            cmd = cmd + ['--bids']
            if options.bids_options:
                print('bids_options: ')
                print(options.bids_options)
                cmd = cmd + options.bids_options

        if options.overwrite:
            cmd = cmd + ['--overwrite']

        if options.datalad:
            cmd = cmd + ['--datalad']

        if options.minmeta:
            cmd = cmd + ['--minmeta']

        if options.with_prov:
            cmd = cmd + ['--with-prov']

        if options.random_seed:
            cmd = cmd + ['--random-seed', str(options.random_seed)]

        if options.command:
            cmd = cmd + ['--command', options.command]

        if options.grouping:
            cmd = cmd + ['--grouping', options.grouping]

        if options.locator:
            cmd = cmd + ['--locator', options.locator]

        if options.session:
            cmd = cmd + ['--ses', options.session]

        if options.dcmconfig:
            cmd = cmd + ['--dcmconfig', options.dcmconfig]

        if options.queue:
            cmd = cmd + ['--queue', options.queue]

        if options.queue_args:
            cmd = cmd + ['--queue-args', options.queue_args]

        if options.anon_cmd:
            cmd = cmd + ['--anon-cmd', options.anon_cmd]

        if options.subjects:
            cmd = cmd + ['--subjects'] + options.subjects

        print(Gstr_title)
        print('Version: %s' % self.get_version())

        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = options.git_user_name
        env["GIT_AUTHOR_EMAIL"] = options.git_user_email
        env["GIT_COMMITTER_NAME"] = options.git_user_name
        env["GIT_COMMITTER_EMAIL"] = options.git_user_email

        print(f'Command: {" ".join(map(str, cmd))}')

        subprocess.run(cmd, check=True, env=env)

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
