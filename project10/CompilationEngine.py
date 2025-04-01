"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output.txt stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output.txt. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output.txt stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.tokenizer = input_stream
        self.output = output_stream
        self.indentation_level = 0

    def get_indentation(self) -> str:
        return "  " * self.indentation_level

    def write_token(self) -> None:
        """Writes the current token to the output.txt stream."""
        token_type = self.tokenizer.token_type()
        indent = self.get_indentation()
        if token_type == "KEYWORD":
            self.output.write(f"{indent}<keyword> {self.tokenizer.keyword()} </keyword>\n")
        elif token_type == "SYMBOL":
            symbol = self.tokenizer.symbol()
            if symbol == "<":
                symbol = "&lt;"
            elif symbol == ">":
                symbol = "&gt;"
            elif symbol == "&":
                symbol = "&amp;"
            self.output.write(f"{indent}<symbol> {symbol} </symbol>\n")
        elif token_type == "IDENTIFIER":
            self.output.write(f"{indent}<identifier> {self.tokenizer.identifier()} </identifier>\n")
        elif token_type == "INT_CONST":
            self.output.write(f"{indent}<integerConstant> {self.tokenizer.int_val()} </integerConstant>\n")
        elif token_type == "STRING_CONST":
            self.output.write(f"{indent}<stringConstant> {self.tokenizer.string_val()} </stringConstant>\n")

    def write_opening_tag(self, tag: str) -> None:
        self.output.write(f"{self.get_indentation()}<{tag}>\n")
        self.indentation_level += 1

    def write_closing_tag(self, tag: str) -> None:
        self.indentation_level -= 1
        self.output.write(f"{self.get_indentation()}</{tag}>\n")

    def advance_and_write(self) -> None:
        """Advances the tokenizer and writes the token."""
        self.write_token()
        self.tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.write_opening_tag("class")
        self.advance_and_write()
        self.advance_and_write()
        self.advance_and_write()
        while self.tokenizer.keyword() in {"static", "field"}:
            self.compile_class_var_dec()
        while self.tokenizer.keyword() in {"constructor", "function", "method"}:
            self.compile_subroutine()
        self.advance_and_write()
        self.write_closing_tag("class")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        self.write_opening_tag("classVarDec")
        self.advance_and_write()
        self.advance_and_write()
        self.advance_and_write()
        while self.tokenizer.symbol() == ",":
            self.advance_and_write()
            self.advance_and_write()
        self.advance_and_write()
        self.write_closing_tag("classVarDec")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        self.write_opening_tag("subroutineDec")
        self.advance_and_write()
        self.advance_and_write()
        self.advance_and_write()
        self.advance_and_write()
        self.compile_parameter_list()
        self.advance_and_write()
        self.compile_subroutine_body()
        self.write_closing_tag("subroutineDec")

    def compile_subroutine_body(self) -> None:
        """Compiles a subroutine body."""
        self.write_opening_tag("subroutineBody")
        self.advance_and_write()
        while self.tokenizer.keyword() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.advance_and_write()
        self.write_closing_tag("subroutineBody")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        self.write_opening_tag("parameterList")
        if self.tokenizer.token_type() != "SYMBOL" or self.tokenizer.symbol() != ")":
            self.advance_and_write()
            self.advance_and_write()
            while self.tokenizer.symbol() == ",":
                self.advance_and_write()
                self.advance_and_write()
                self.advance_and_write()
        self.write_closing_tag("parameterList")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        self.write_opening_tag("varDec")
        self.advance_and_write()
        self.advance_and_write()
        self.advance_and_write()
        while self.tokenizer.symbol() == ",":
            self.advance_and_write()
            self.advance_and_write()
        self.advance_and_write()
        self.write_closing_tag("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        self.write_opening_tag("statements")
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
        self.write_closing_tag("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.write_opening_tag("doStatement")
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ".":
            self.write_token()
            self.tokenizer.advance()
            self.write_token()
            self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.compile_expression_list()
        self.write_token()
        self.tokenizer.advance()
        self.write_token()
        self.tokenizer.advance()
        self.write_closing_tag("doStatement")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.write_opening_tag("letStatement")
        self.advance_and_write()
        self.advance_and_write()
        if self.tokenizer.symbol() == "[":
            self.advance_and_write()
            self.compile_expression()
            self.advance_and_write()
        self.advance_and_write()
        self.compile_expression()
        self.advance_and_write()
        self.write_closing_tag("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.write_opening_tag("whileStatement")
        self.advance_and_write()
        self.advance_and_write()
        self.compile_expression()
        self.advance_and_write()
        self.advance_and_write()
        self.compile_statements()
        self.advance_and_write()
        self.write_closing_tag("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.write_opening_tag("returnStatement")
        self.advance_and_write()
        if self.tokenizer.token_type() != "SYMBOL" or self.tokenizer.symbol() != ";":
            self.compile_expression()
        self.advance_and_write()
        self.write_closing_tag("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.write_opening_tag("ifStatement")
        self.advance_and_write()
        self.advance_and_write()
        self.compile_expression()
        self.advance_and_write()
        self.advance_and_write()
        self.compile_statements()
        self.advance_and_write()
        if self.tokenizer.current_token == "else":
            self.compile_else()
        self.write_closing_tag("ifStatement")


    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        self.write_opening_tag("expression")
        self.compile_term()
        while self.tokenizer.current_token in ["+", "-", "*", "/", "&", "|", "<", ">", "=", "~", "^", "#"]:
            self.advance_and_write()
            self.compile_term()
        self.write_closing_tag("expression")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        self.write_opening_tag("term")
        token_type = self.tokenizer.token_type()

        if token_type == "INT_CONST":
            self.advance_and_write()
        elif token_type == "STRING_CONST":
            self.advance_and_write()
        elif token_type == "KEYWORD" and self.tokenizer.keyword() in {"true", "false", "null", "this"}:
            self.advance_and_write()
        elif token_type == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.advance_and_write()
            self.compile_expression()
            self.advance_and_write()
        elif token_type == "SYMBOL" and self.tokenizer.symbol() in {"-", "~", "#","^"}:
            self.advance_and_write()
            self.compile_term()
        elif token_type == "IDENTIFIER":
            self.advance_and_write()
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
                self.advance_and_write()
                self.compile_expression()
                self.advance_and_write()
            elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "(":
                self.advance_and_write()
                self.compile_expression_list()
                self.advance_and_write()
            elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ".":
                self.advance_and_write()
                self.advance_and_write()
                self.advance_and_write()
                self.compile_expression_list()
                self.advance_and_write()
        self.write_closing_tag("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        self.write_opening_tag("expressionList")
        if self.tokenizer.token_type() != "SYMBOL" or self.tokenizer.symbol() != ")":
            self.compile_expression()
            while self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.write_token()
                self.tokenizer.advance()
                self.compile_expression()
        self.write_closing_tag("expressionList")

    def compile_else(self):
        self.advance_and_write()
        self.advance_and_write()
        self.compile_statements()
        self.advance_and_write()
