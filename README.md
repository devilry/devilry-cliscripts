Devilry command line scripts. These scripts use the Devilry RESTful API to perform various tasks from the command line on any machine with Python installed.


## Requirements

- Python 2.6+
- [devilryrestfullib](https://github.com/devilry/devilryrestfullib). Just follow the link to their wiki for install instructions.


## Install

No install is required (except for the requirements above). You just run the scripts.


## Usage

All of the scripts can be exectuted with ``--help`` for details on what they do
and how they work. Example:

    $ ./period-overview-csv.py --help

All of the scripts require login, so you always need to supply ``-url`` and
``--user``. Additionally, some login methods may vary, so you may have to
specify ``--loginprofile`` or ``--usernamefield`` and ``--passwordfield``.

For example, to show an overview of all students on ``inf1010.2012v`` at
university of oslo, you would use:

    ./period-overview.py --url https://devilry.ifi.uio.no --user someuser --loginprofile uio --period inf1010.2012v

Your user (``someuser`` in the example) will, of course, have to have
permission to get this data for it to work.
