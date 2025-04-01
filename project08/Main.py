import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter

import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(input_file: typing.TextIO, output_file: typing.TextIO, bootstrap: bool) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
        bootstrap (bool): if this is True, the current file is the
            first file we are translating, and bootstrap code should be written.
    """
    # Create the CodeWriter instance inside translate_file
    code_writer = CodeWriter(output_file)

    # Write bootstrap code only for the first file (bootstrap is True)
    if bootstrap:
        code_writer.write_init()

    # Initialize Parser with the input stream
    parser = Parser(input_file)
    file_name = getattr(input_file, 'name', 'Unknown')
    code_writer.set_file_name(file_name)

    # Process each command in the input file
    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()

        if command_type == "C_ARITHMETIC":
            code_writer.write_arithmetic(parser.arg1())
        elif command_type in {"C_PUSH", "C_POP"}:
            code_writer.write_push_pop(command_type, parser.arg1(), int(parser.arg2()))
        elif command_type == "C_LABEL":
            code_writer.write_label(parser.arg1())
        elif command_type == "C_GOTO":
            code_writer.write_goto(parser.arg1())
        elif command_type == "C_IF":
            code_writer.write_if(parser.arg1())
        elif command_type == "C_FUNCTION":
            code_writer.write_function(parser.arg1(), int(parser.arg2()))
        elif command_type == "C_RETURN":
            code_writer.write_return()
        elif command_type == "C_CALL":
            code_writer.write_call(parser.arg1(), parser.arg2())


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)
            bootstrap = False
