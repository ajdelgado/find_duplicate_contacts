# find_duplicate_contacts

## Requirements

See the requirements.txt file for required Python modules.
Save the contacts as individual (one contact per file) vCard files in an isolated directory.

## Installation

### Linux

  `sudo python3 setup.py install`

### Windows (from PowerShell)

  `& $(where.exe python).split()[0] setup.py install`

## Usage
- Save the contacts as individual (one contact per file) vCard files in an isolated directory, pass this directory with the *--directory* option.
- Those completely equal, except for some list of keys (see the *ignore_fileds* variable), will be directly moved to the *--duplicates-destination* folder inside the *--directory*.
- Those with equal full name, will be show and a prompt will ask you to keep one of the contact cards or just do nothing with them.

```find_duplicate_contacts.py [OPTIONS]```

Options:
  -d, --debug-level [CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET]
                                  Set the debug level for the standard output.
  -l, --log-file TEXT             File to store all debug messages.
  -f, --directory TEXT            Directory containing vCard files to check.
                                  [required]
  -D, --duplicates-destination TEXT
                                  Directory to move duplicates files, relative
                                  to the directory containing the vCards. Default: duplicates
  --config FILE                   Read configuration from FILE.
  --help                          Show this message and exit.```

## License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)