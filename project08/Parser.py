"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line's end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        all_lines = input_file.read().splitlines()
        clean_lines = []
        for line in all_lines:
            line = line.split("//")[0].strip()
            if line != "":
                clean_lines.append(line)
        self.input_lines = clean_lines
        self.current_command = None
        self.current_index = 0

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        more_commands = False
        if self.current_index < len(self.input_lines):
            more_commands = True
        return more_commands

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        # Your code goes here!
        if self.has_more_commands():
            self.current_command = self.input_lines[self.current_index].strip()
            if "//" in self.current_command:
                self.current_command = self.current_command.split('//')[0].replace(" ", "")
            self.current_index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # Define arithmetic commands
        arithmetic_commands = {
            "add", "sub", "neg", "and", "or", "not", "shiftleft", "shiftright", "eq", "gt", "lt"
        }

        # Get the first part of the current command
        command = self.current_command.split()[0]

        # Map commands to their types
        if command in arithmetic_commands:
            return "C_ARITHMETIC"
        elif command == "push":
            return "C_PUSH"
        elif command == "pop":
            return "C_POP"
        elif command == "label":
            return "C_LABEL"
        elif command == "goto":
            return "C_GOTO"
        elif command == "if-goto":  # Corrected check for "if-goto"
            return "C_IF"
        elif command == "function":
            return "C_FUNCTION"
        elif command == "return":
            return "C_RETURN"
        elif command == "call":
            return "C_CALL"
        else:
            raise ValueError(f"Unknown command: {self.current_command}")

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        # Your code goes here!
        if self.command_type() != "C_RETURN":
            if self.command_type() == "C_ARITHMETIC":
                return self.current_command
            else:
                return self.current_command.split()[1]
        else:
            raise ValueError("arg1 should not be called for C_RETURN type command.")

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        # Your code goes here!
        if self.command_type() == "C_PUSH" or self.command_type() == "C_POP" \
                or self.command_type() == "C_FUNCTION" or self.command_type() == "C_CALL":
            return self.current_command.split()[2]
        else:
            raise ValueError("arg2 should only be called for C_PUSH, C_POP, C_FUNCTION, or C_CALL.")