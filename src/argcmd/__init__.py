from abc import ABCMeta, abstractmethod
import argparse
import os
import sys
from gettext import gettext as _
from typing import IO, List, Optional


class Command(metaclass=ABCMeta):
    """
    AbstractBaseClass for any command
    """

    def __init__(self) -> None:
        self._subparsers = {}

    def _get_command_name(self) -> str:
        """
        Get the name of this Command.  Respects the _COMMAND_NAME attribute, if
        present, otherwise derives a name from the class name, removing the
        trailing "Command" suffix if present. In all cases, the name is
        converted to lowercase.
        """

        # if the cmd class has a '_COMMAND_NAME_' attribute, use that
        name = getattr(self, '_COMMAND_NAME_', None)

        if name is None:
            # otherwise, use the class's name, lowercased, with the "Command" suffix removed
            name = self.__class__.__name__
            if name.endswith('Command'):
                name = name[:-7]
                assert len(name) > 0, _("Command classes must not be called simply 'Command', if you want to derive their name.  Set _COMMAND_NAME_ explicitly.")

        return name.lower()

    def _get_command_help(self) -> str:
        """
        Get the help for this Command. Respects the _COMMAND_HELP attribute, if
        present, otherwise returns the docuemntation string for the class, if available.
        Otherwise, returns an empty string.
        """

        help = getattr(self, '_COMMAND_HELP_', None)

        if help is None:
            help = self.__doc__ or ''

        return help

    @abstractmethod
    def augment_subparsers(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        subparser = subparsers.add_parser(
            self._get_command_name(),
            help=self._get_command_help()
        )
        subparser.set_defaults(func=self.execute)
        return subparser

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        raise NotImplementedError()


class CommandRegistry:
    def __init__(self) -> None:
        """
        Create a new command registry.
        """
        self.commands = {}

    def add(self, cmd: Command, name: Optional[str] = None) -> None:
        """
        Register a command with the registry.  If name is given, the command will be
        registered under that name.  Otherwise, the class's name will be used, lowercased,
        with the "Command" suffix removed.
        """

        name = cmd._get_command_name()
        self.commands[name] = cmd

    def execute(self,
        argv0: Optional[str] = None,
        args: Optional[List[str]] = None,
        err_stream: Optional[IO[str]] = None
    ) -> int:
        """
        Parse the given arguments, and execute the appropriate command.  Print usage
        help to err_stream if the arguments are invalid.  If err_stream is not given,
        print to sys.stderr instead.
        """

        if argv0 is None:
            argv0 = sys.argv[0]

        if args is None:
            args = sys.argv[1:]

        parser = argparse.ArgumentParser()
        parser.set_defaults(func=None, argv0=argv0)

        subparsers = parser.add_subparsers(
            metavar='command',
            required=True,
            help=_('Choose one of the following commands:'),
        )
        for cmd_name, cmd in self.commands.items():
            cmd.augment_subparsers(subparsers)

        args = parser.parse_args(sys.argv[1:])

        if args.func is not None:
            return args.func(args)
        else:
            parser.print_help(file=err_stream)
            return os.EX_USAGE
