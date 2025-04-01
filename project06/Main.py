"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")
    shift_table = {
        "D>>": "0010000",
        "D<<": "0110000",
        "A>>": "0000000",
        "A<<": "0100000",
        "M>>": "1000000",
        "M<<": "1100000",
    }
    parser = Parser(input_file)
    symbol_table = SymbolTable()
    current_index = 0
    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()

        if command_type == "L_COMMAND":
            symbol_table.add_entry(parser.symbol(), current_index)
        else:
            current_index += 1
    input_file.seek(0)
    parser = Parser(input_file)
    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        if command_type == "A_COMMAND":
            symbol = parser.symbol()
            if symbol.isdigit():
                output_file.write(f"0{format(int(symbol), '015b')}\n")
            else:
                if not symbol_table.contains(symbol):
                    symbol_table.add_entry(symbol, symbol_table.next_variable_address)
                    symbol_table.next_variable_address += 1
                output_file.write(f"{format(symbol_table.get_address(symbol), '016b')}\n")
        elif command_type == "C_COMMAND":
            dest = Code.dest(parser.dest())
            comp = Code.comp(parser.comp())
            jump = Code.jump(parser.jump())
            if parser.comp() in shift_table:
                output_file.write(f"101{comp}{dest}{jump}\n")
            else:
                output_file.write(f"111{comp}{dest}{jump}\n")

if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
