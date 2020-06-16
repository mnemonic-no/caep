# CAEP

config module, supports loading config from ini, environment and arguments

The configuration presedence are (from lowest to highest):
* argparse default
* ini file
* environment variable
* command line argument

# Config

Arguments are parsed in two phases. First, it will look for the argument --config argument
which can be used to specify an alternative location for the ini file. If not --config argument
is given it will look for an ini file in the following locations (~/.config has presedence):

- ~/.config/<CONFIG_ID>/<CONFIG_FILE_NAME> (or directory specified by XDG_CONFIG_HOME)
- /etc/<CONFIG_FILE_NAME>

The ini file can contain a "[DEFAULT]" section that will be used for all configurations.
In addition it can have a section that corresponds with <SECTION_NAME> that for
specific configuration, that will over override config from DEFAULT

# Environment variables

The configuration step will also look for environment variables in uppercase and
with "-" replaced with "_". For the example below it will lookup the following environment
variables:

- $NUMBER
- $BOOL
- $STR_ARG

Example:

```
>>> import caep
>>> import argparse
>>> parser = argparse.ArgumentParser("test argparse")
>>> parser.add_argument('--number', type=int, default=1)
>>> parser.add_argument('--bool', action='store_true')
>>> parser.add_argument('--str-arg')
>>> args = caep.config.handle_args(parser, <CONFIG_ID>, <CONFIG_FILE_NAME>, <SECTION_NAME>)
```
