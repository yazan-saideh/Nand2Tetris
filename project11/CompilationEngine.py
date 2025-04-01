from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """
    Compiles Jack code into VM commands.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        self.tokenizer = input_stream
        self.vm_writer = VMWriter()
        self.vm_writer.init(output_stream)
        self.label_counter = 0
        self.symbol_table = SymbolTable()
        self.class_name = None
        self.num_of_args = 0
        self.subroutine_type = None

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.tokenizer.advance()  # 'class'
        self.class_name = self.tokenizer.identifier()
        self.tokenizer.advance()  # Class name
        self.tokenizer.advance()  # '{'

        # Compile all class variable declarations
        while self.tokenizer.keyword() in {"static", "field"}:
            self.compile_class_var_dec()

        # Compile all subroutine declarations
        while self.tokenizer.keyword() in {"constructor", "function", "method"}:
            self.compile_subroutine()

        self.tokenizer.advance()  # '}'

    def compile_class_var_dec(self) -> None:
        """Compiles a static or field declaration."""
        kind = self.tokenizer.keyword().upper()  # 'static' or 'field'
        self.tokenizer.advance()  # 'var'
        var_type = self.tokenizer.identifier()  # Type
        self.tokenizer.advance()  # Type

        while True:
            var_name = self.tokenizer.identifier()  # Variable name
            # Add the variable to the symbol table as VAR kind
            self.symbol_table.define(var_name, var_type, kind)
            print(f"Added variable to symbol table: {var_name}, type: {var_type}, kind: VAR")
            self.tokenizer.advance()  # Advance past variable name
            if self.tokenizer.symbol() != ",":
                break  # No more variables in this declaration
            self.tokenizer.advance()  # ','

        self.tokenizer.advance()  # ';'

    def compile_subroutine(self) -> None:
        """Compiles a constructor, function, or method."""
        self.subroutine_type = self.tokenizer.keyword()  # 'constructor', 'function', or 'method'
        self.label_counter = 0
        self.tokenizer.advance()  # Advance past 'constructor', 'function', or 'method'
        self.tokenizer.advance()  # Return type (e.g., 'void', 'int')
        subroutine_name = self.tokenizer.identifier()  # Subroutine name
        self.tokenizer.advance()  # Advance past the subroutine name
        self.tokenizer.advance()  # '('

        # Start a new subroutine scope
        self.symbol_table.start_subroutine()
        if self.subroutine_type == "method":
            self.symbol_table.define("this", self.class_name, "ARG")  # Define 'this' for methods

        # Compile the parameter list
        self.compile_parameter_list()
        self.tokenizer.advance()  # ')'

        self.tokenizer.advance()  # '{'

        # Compile all local variable declarations
        while self.tokenizer.keyword() == "var":
            self.compile_var_dec()

        # Count the number of local variables now
        num_locals = self.symbol_table.var_count("VAR")
        print(f"Compiling function {self.class_name}.{subroutine_name} with {num_locals} local variables")

        # Write the function declaration with the correct number of locals
        self.vm_writer.write_function(f"{self.class_name}.{subroutine_name}", num_locals)

        # Handle constructor and method-specific initialization
        if self.subroutine_type == "constructor":
            num_fields = self.symbol_table.var_count("FIELD")
            self.vm_writer.write_push("CONSTANT", num_fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)
        elif self.subroutine_type == "method":
            self.vm_writer.write_push("ARGUMENT", 0)
            self.vm_writer.write_pop("POINTER", 0)

        # Compile the statements in the body
        self.compile_subroutine_body()

    def compile_parameter_list(self) -> None:
        """Compiles a parameter list."""
        if self.tokenizer.symbol() == ")":
            return

        while True:
            param_type = self.tokenizer.identifier()
            self.tokenizer.advance()  # Type
            param_name = self.tokenizer.identifier()
            self.symbol_table.define(param_name, param_type, "ARG")
            self.tokenizer.advance()  # Variable name

            if self.tokenizer.symbol() != ",":
                break
            self.tokenizer.advance()  # ','

    def compile_subroutine_body(self) -> None:
        """Compiles a subroutine body."""
         # '{'

        # Compile all local variable declarations

        # Compile all statements within the subroutine
        self.compile_statements()

        self.tokenizer.advance()  # '}'

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.tokenizer.advance()  # 'var'
        var_type = self.tokenizer.identifier()  # Type
        self.tokenizer.advance()  # Type

        while True:
            var_name = self.tokenizer.identifier()  # Variable name
            # Add the variable to the symbol table as VAR kind
            self.symbol_table.define(var_name, var_type, "VAR")
            print(f"Defined local variable: {var_name}, type: {var_type}, kind: VAR")
            self.tokenizer.advance()  # Advance past variable name
            if self.tokenizer.symbol() != ",":
                break
            self.tokenizer.advance()  # ','

        self.tokenizer.advance()  # ';'

    def compile_statements(self) -> None:
        """Compiles a sequence of statements."""
        while self.tokenizer.keyword() in {"let", "if", "while", "do", "return"}:
            if self.tokenizer.keyword() == "let":
                self.compile_let()

            elif self.tokenizer.keyword() == "if":
                self.compile_if()
            elif self.tokenizer.keyword() == "while":
                self.compile_while()
            elif self.tokenizer.keyword() == "do":
                self.compile_do()
            elif self.tokenizer.keyword() == "return":
                self.compile_return()
            if self.tokenizer.keyword() == ";":
                self.tokenizer.advance()

    # Additional methods (compile_if, compile_while, compile_do, etc.) remain the same.

    def compile_if(self) -> None:
        """Compiles an if statement."""
        true_label = f"IF_TRUE{self.label_counter}"
        false_label = f"IF_FALSE{self.label_counter}"
        end_label = f"IF_END{self.label_counter}"
        self.label_counter += 1

        self.tokenizer.advance()  # 'if'
        self.tokenizer.advance()  # '('
        self.compile_expression()
        self.vm_writer.write_if(true_label)  # If true, jump to IF_TRUE
        self.vm_writer.write_goto(false_label)  # Else, jump to IF_FALSE
        self.vm_writer.write_label(true_label)
        self.tokenizer.advance()  # ')'
        self.tokenizer.advance()  # '{'
        self.compile_statements()
        self.tokenizer.advance()  # '}'

        if self.tokenizer.keyword() == "else":
            self.vm_writer.write_goto(end_label)
            self.vm_writer.write_label(false_label)
            self.tokenizer.advance()  # 'else'
            self.tokenizer.advance()  # '{'
            self.compile_statements()
            self.tokenizer.advance()  # '}'
            self.vm_writer.write_label(end_label)
        else:
            self.vm_writer.write_label(false_label)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        start_label = f"WHILE_START_{self.label_counter}"
        end_label = f"WHILE_END_{self.label_counter}"
        self.label_counter += 1

        self.vm_writer.write_label(start_label)
        self.tokenizer.advance()  # 'while'
        self.tokenizer.advance()  # '('
        self.compile_expression()
        self.vm_writer.write_arithmetic("not")  # Negate condition
        self.vm_writer.write_if(end_label)  # Exit loop if condition is false
        self.tokenizer.advance()  # ')'
        self.tokenizer.advance()  # '{'
        self.compile_statements()
        self.tokenizer.advance()  # '}'
        self.vm_writer.write_goto(start_label)  # Jump back to start of loop
        self.vm_writer.write_label(end_label)

    def compile_do(self) -> None:

        self.tokenizer.advance()  # 'do'
        identifier = self.tokenizer.identifier()  # Subroutine or class name
        self.tokenizer.advance()  # Advance past the identifier

        # Compile the subroutine call
        self.compile_subroutine_call(identifier)

        # Discard the return value of the subroutine
        self.vm_writer.write_pop("TEMP", 0)

        self.tokenizer.advance()  # ';'

    def compile_return(self) -> None:
        """Compiles a return statement."""
        if self.subroutine_type == "constructor":
            self.tokenizer.advance()
            self.tokenizer.advance()  # 'return'
        else:
            self.tokenizer.advance()
        if self.tokenizer.symbol() != ";":
            self.compile_expression()
        else:
            if self.subroutine_type == "constructor":
                self.tokenizer.advance()
                self.vm_writer.write_push("POINTER", 0)  # Return void (0)
            else:
                self.vm_writer.write_push("CONSTANT", 0)  # Return void (0)
        self.vm_writer.write_return()

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()

        while self.tokenizer.symbol() in {"+", "-", "*", "/", "&", "|", "<", ">", "="}:
            operator = self.tokenizer.symbol()
            self.tokenizer.advance()  # Operator
            self.compile_term()
            operator_map = {
                "+": "add",
                "-": "sub",
                "*": "call Math.multiply 2",
                "/": "call Math.divide 2",
                "&": "and",
                "|": "or",
                "<": "lt",
                ">": "gt",
                "=": "eq",
            }
            self.vm_writer.write_arithmetic(operator_map[operator])

    def compile_term(self) -> None:
        """Compiles a term."""
        token_type = self.tokenizer.token_type()

        if token_type == "INT_CONST":
            self.vm_writer.write_push("CONSTANT", self.tokenizer.int_val())
            self.tokenizer.advance()
        elif token_type == "KEYWORD":  # Keywords like true, false, null, this
            keyword = self.tokenizer.keyword()
            if keyword == "true":
                self.vm_writer.write_push("CONSTANT", 0)
                self.vm_writer.write_arithmetic("not")
            elif keyword == "false":
                self.vm_writer.write_push("CONSTANT", 0)
            elif keyword == "null":
                self.vm_writer.write_push("CONSTANT", 0)
            self.tokenizer.advance()

        elif token_type == "STRING_CONST":
            string_value = self.tokenizer.string_val()
            self.vm_writer.write_push("CONSTANT", len(string_value))
            self.vm_writer.write_call("String.new", 1)
            for char in string_value:
                self.vm_writer.write_push("CONSTANT", ord(char))
                self.vm_writer.write_call("String.appendChar", 2)
            self.tokenizer.advance()
        elif self.tokenizer.symbol() == "(":
            self.tokenizer.advance()  # '('
            self.compile_expression()
            self.tokenizer.advance()  # ')'
        elif self.tokenizer.symbol() in {"-", "~"}:
            unary_op = self.tokenizer.symbol()
            self.tokenizer.advance()
            self.compile_term()
            unary_map = {"-": "neg", "~": "not"}
            self.vm_writer.write_arithmetic(unary_map[unary_op])
        elif token_type == "IDENTIFIER":
            identifier = self.tokenizer.identifier()
            self.tokenizer.advance()
            if self.tokenizer.symbol() == "[":
                self.tokenizer.advance()  # '['
                self.compile_expression()
                self.tokenizer.advance()  # ']'
                if self.symbol_table.kind_of(identifier).upper() == "VAR":
                    temporary = "local"
                if self.symbol_table.kind_of(identifier).upper() == "FIELD":
                    temporary = "this"
                if self.symbol_table.kind_of(identifier).upper() == "ARG":
                    temporary = "argument"
                self.vm_writer.write_push(temporary,
                                          self.symbol_table.index_of(identifier))
                self.vm_writer.write_arithmetic("add")
                self.vm_writer.write_pop("POINTER", 1)
                self.vm_writer.write_push("THAT", 0)
            elif self.tokenizer.symbol() in {"(", "."}:
                self.compile_subroutine_call(identifier)
            else:
                kind = self.symbol_table.kind_of(identifier)
                index = self.symbol_table.index_of(identifier)

                if kind == "ARG":
                    segment = "argument"
                elif kind == "VAR":
                    segment = "local"
                elif kind == "FIELD":
                    segment = "this"
                elif kind == "STATIC":
                    segment = "static"
                else:
                    raise ValueError(f"Unknown variable kind: {kind}")

                self.vm_writer.write_push(segment, index)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        num_args = 0
        if self.tokenizer.symbol() != ")":
            self.compile_expression()
            num_args += 1
            while self.tokenizer.symbol() == ",":
                self.tokenizer.advance()  # ','
                self.compile_expression()
                num_args += 1
        return num_args

    def compile_subroutine_call(self, identifier: str) -> None:
        """Compiles a subroutine call."""
        num_args = 0
        subroutine_name = ""

        # Check if it's an external method or function call
        if self.tokenizer.symbol() == ".":  # External or object method
            self.tokenizer.advance()  # '.'
            subroutine_part = self.tokenizer.identifier()  # Subroutine name
            self.tokenizer.advance()  # Advance past subroutine name

            if identifier in {"Memory", "Array", "String", "Keyboard", "Screen", "Output", "Sys"}:
                # Static class method
                subroutine_name = f"{identifier}.{subroutine_part}"
                # Push `pointer 0` ONLY if the method requires it
                if identifier == "Memory" and subroutine_part in {"deAlloc"}:
                    self.vm_writer.write_push("POINTER", 0)
            elif self.symbol_table.kind_of(identifier):  # Object method
                kind = self.symbol_table.kind_of(identifier)
                segment = (
                    "local" if kind == "VAR"
                    else "argument" if kind == "ARG"
                    else "this" if kind == "FIELD"
                    else kind.lower()
                )
                index = self.symbol_table.index_of(identifier)
                self.vm_writer.write_push(segment, index)  # Push object reference (this)
                num_args += 1  # Increment num_args for the object reference
                subroutine_name = f"{self.symbol_table.type_of(identifier)}.{subroutine_part}"
            else:  # Static user-defined class method
                subroutine_name = f"{identifier}.{subroutine_part}"
        else:  # Local method (e.g., `do myLocalMethod();`)
            subroutine_name = f"{self.class_name}.{identifier}"
            self.vm_writer.write_push("POINTER", 0)  # Push 'this'
            num_args += 1

        self.tokenizer.advance()  # '('
        num_args += self.compile_expression_list()  # Compile arguments
        self.tokenizer.advance()  # ')'

        # Write the call command
        self.vm_writer.write_call(subroutine_name, num_args)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.tokenizer.advance()  # 'let'
        var_name = self.tokenizer.identifier()  # Variable name
        self.tokenizer.advance()  # Advance past the variable name
        is_array = False

        if self.tokenizer.symbol() == "[":
            is_array = True
            self.tokenizer.advance()  # '['
            self.compile_expression()  # Compile the index
            self.tokenizer.advance()  # ']'
            # Push the base address of the array
            kind = self.symbol_table.kind_of(var_name)
            segment = "this" if kind == "FIELD" else kind.lower()
            if kind == "ARG":
                segment = "argument"
            elif kind == "VAR":
                segment = "local"
            elif kind == "FIELD":
                segment = "this"
            self.vm_writer.write_push(segment, self.symbol_table.index_of(var_name))
            self.vm_writer.write_arithmetic("add")

        self.tokenizer.advance()  # '='
        self.compile_expression()  # Compile the right-hand side
        self.tokenizer.advance()  # ';'

        if is_array:
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            kind = self.symbol_table.kind_of(var_name)
            segment = "this" if kind == "FIELD" else kind.lower()
            if segment == "var":
                segment = "local"
            if segment == "arg":
                segment = "argument"
            self.vm_writer.write_pop(segment, self.symbol_table.index_of(var_name))