"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import os


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_stream = output_stream
        self.counter = 0
        self.file_name = ""
        self.current_function = ""

    def write_init(self) -> None:
        """
        Writes the bootstrap code that initializes the VM.
        Sets SP=256 and calls Sys.init.
        """
        # Initialize SP to 256
        self.output_stream.write("// Bootstrap code\n")
        self.output_stream.write("@256\nD=A\n@SP\nM=D\n")

        # Call Sys.init
        self.write_call("Sys.init", 0)
    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))

        self.file_name = os.path.splitext(os.path.basename(filename))[0]

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        if command == "add":
            self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\n"
                                     "@SP\nM=M-1\nA=M\nD=M+D\n"
                                     "@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == "sub":
            self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\n"
                                     "@SP\nM=M-1\nA=M\nD=M-D\n"
                                     "@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == "and":
            self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\n"
                                     "@SP\nM=M-1\nA=M\nD=M&D\n"
                                     "@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == "or":
            self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\n"
                                     "@SP\nM=M-1\nA=M\nD=M|D\n"
                                     "@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == "neg":
            self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\nD=-D\n"
                                     "@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == "not":
            self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\nD=!D\n"
                                     "@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == "shiftleft":
            self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\nD=D<<\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == "shiftright":
            self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\nD=D>>\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command in ["eq", "gt", "lt"]:
            self.comparison(command)

    def comparison(self, command: str) -> None:
        """
        Writes assembly code for comparison commands (eq, lt, gt).
        Handles all cases of signed comparison explicitly and efficiently.
        """
        true_label = f"TRUE{self.counter}"
        false_label = f"FALSE{self.counter}"
        end_label = f"END{self.counter}"
        self.counter += 1

        asm_code = (
            "@SP\nM=M-1\nA=M\nD=M\n@R13\nM=D\n"
            "@SP\nM=M-1\nA=M\nD=M\n@R14\nM=D\n"
        )
        asm_code += (
            "@R14\nD=M\n"
            f"@{false_label if command == 'gt' else true_label}\nD;JLT\n"
        )
        asm_code += (
            "@R13\nD=M\n"
            f"@{true_label if command == 'gt' else false_label}\nD;JLT\n"
        )
        asm_code += (
            "@R14\nD=M\n@R13\nD=D-M\n"
        )
        if command == "eq":
            asm_code += f"@{true_label}\nD;JEQ\n"
        elif command == "lt":
            asm_code += f"@{true_label}\nD;JLT\n"
        elif command == "gt":
            asm_code += f"@{true_label}\nD;JGT\n"
        asm_code += f"@{false_label}\n0;JMP\n"
        asm_code += (
            f"({true_label})\n@SP\nA=M\nM=-1\n@{end_label}\n0;JMP\n"
            f"({false_label})\n@SP\nA=M\nM=0\n@{end_label}\n0;JMP\n"
            f"({end_label})\n@SP\nM=M+1\n"
        )
        self.output_stream.write(asm_code)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        segment_map = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        if command == "C_PUSH":
            if segment == "constant":
                self.output_stream.write(f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "static":
                self.output_stream.write(f"@{self.file_name}.{index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "temp":
                self.output_stream.write(f"@{5 + index}\nD=A\n@addr\nM=D\n@addr\nA=M\nD=M\n@SP\n"
                                         f"A=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "pointer":
                if index == 0:
                    address = "THIS"
                elif index == 1:
                    address = "THAT"
                else:
                    raise ValueError("Invalid pointer index, should be only 0 or 1.")
                self.output_stream.write(f"@{address}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            else:
                self.output_stream.write(
                    f"@{index}\nD=A\n@{segment_map[segment]}\nA=M\nD=A+D\n@addr\nM=D\n"
                    f"@addr\nA=M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        elif command == "C_POP":
            if segment == "static":
                self.output_stream.write(f"@SP\nM=M-1\nA=M\nD=M\n@{self.file_name}.{index}\nM=D\n")
            elif segment == "temp":
                self.output_stream.write(f"@{5 + index}\nD=A\n@addr\nM=D\n@SP\nM=M-1\n"
                                         f"@SP\nA=M\nD=M\n@addr\nA=M\nM=D\n")
            elif segment == "pointer":
                if index == 0:
                    address = "THIS"
                else:
                    address = "THAT"
                self.output_stream.write(
                    f"@SP\nM=M-1\n@SP\nA=M\nD=M\n@{address}\nM=D\n"
                )
            else:
                self.output_stream.write(
                    f"@{index}\nD=A\n@{segment_map[segment]}\nA=M\nD=A+D\n@addr\nM=D\n"
                    f"@SP\nM=M-1\n@SP\nA=M\nD=M\n@addr\nA=M\nM=D\n"
                )

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command.
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        unique_label = f"{self.file_name}${label}"
        self.output_stream.write(f"({unique_label})\n")

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        unique_label = f"{self.file_name}${label}"
        self.output_stream.write(f"@{unique_label}\n0;JMP\n")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        unique_label = f"{self.file_name}${label}"
        self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\n")
        self.output_stream.write(f"@{unique_label}\nD;JNE\n")

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command.
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.current_function = function_name

        # Write the function entry label
        self.output_stream.write(f"({function_name})\n")

        # Initialize local variables to 0
        for _ in range(n_vars):
            self.output_stream.write("@SP\nA=M\nM=0\n@SP\nM=M+1\n")

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command.
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        return_address = f"{self.file_name}.{self.current_function}$ret.{self.counter}"
        self.counter += 1

        # Push return address
        self.output_stream.write(f"@{return_address}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        # Push LCL, ARG, THIS, THAT (save caller's state)
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            self.output_stream.write(f"@{segment}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        # ARG = SP - 5 - n_args
        self.output_stream.write(f"@SP\nD=M\n@5\nD=D-A\n@{n_args}\nD=D-A\n@ARG\nM=D\n")

        # LCL = SP
        self.output_stream.write("@SP\nD=M\n@LCL\nM=D\n")

        # Goto function_name
        self.output_stream.write(f"@{function_name}\n0;JMP\n")

        # Insert return address label
        self.output_stream.write(f"({return_address})\n")

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        self.output_stream.write("@LCL\nD=M\n@R13\nM=D\n")

        # RET = *(FRAME - 5) (store return address in a temporary variable, R14)
        self.output_stream.write("@5\nA=D-A\nD=M\n@R14\nM=D\n")

        # *ARG = pop() (store return value in caller's argument[0])
        self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n")

        # SP = ARG + 1 (reposition SP)
        self.output_stream.write("@ARG\nD=M+1\n@SP\nM=D\n")

        # Restore THAT, THIS, ARG, LCL
        for i, segment in enumerate(["THAT", "THIS", "ARG", "LCL"], start=1):
            self.output_stream.write(f"@R13\nD=M\n@{i}\nA=D-A\nD=M\n@{segment}\nM=D\n")

        # Goto return address
        self.output_stream.write("@R14\nA=M\n0;JMP\n")

