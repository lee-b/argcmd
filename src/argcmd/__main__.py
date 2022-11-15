import argparse
import sys

from . import Command, CommandRegistry


class HelloCommand(Command):
    def augment_subparsers(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        subparser = super().augment_subparsers(subparsers)
        subparser.add_argument('name')
        return subparser

    def execute(self, args: argparse.Namespace) -> int:
        print(f"Hello, {args.name}!")
        print(f"\nToday's greeting was brought to you by {args.argv0}.")


def main():
    cmd = HelloCommand()

    reg = CommandRegistry()
    reg.add(cmd)

    return reg.execute()
