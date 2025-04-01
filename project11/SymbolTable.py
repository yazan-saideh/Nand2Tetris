class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind, and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_scope = {}  # STATIC and FIELD variables
        self.subroutine_scope = {}  # ARG and VAR variables
        self.index_counters = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}
        self.current_class_name = None  # For handling 'this'

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope and resets ARG and VAR counters."""
        self.subroutine_scope = {}
        self.index_counters["ARG"] = 0
        self.index_counters["VAR"] = 0
        print("Subroutine scope reset.")  # Debugging

    def define(self, name: str, type_: str, kind: str) -> None:
        if kind.upper() in {"ARG", "VAR"}:
            self.subroutine_scope[name] = {
                "type": type_,
                "kind": kind.upper(),
                "index": self.index_counters[kind.upper()],
            }
        elif kind.upper() in {"STATIC", "FIELD"}:
            self.class_scope[name] = {
                "type": type_,
                "kind": kind.upper(),
                "index": self.index_counters[kind.upper()],
            }
        else:
            raise ValueError(f"Invalid kind: {kind}")


        self.index_counters[kind.upper()] += 1
    def var_count(self, kind: str) -> int:
        """Returns the number of variables of the given kind already defined."""
        kind = kind.upper()
        if kind in {"STATIC", "FIELD"}:
            count = sum(1 for entry in self.class_scope.values() if entry["kind"] == kind)
        elif kind in {"ARG", "VAR"}:
            count = sum(1 for entry in self.subroutine_scope.values() if entry["kind"] == kind)
        else:
            raise ValueError(f"Invalid kind: {kind}. Must be one of STATIC, FIELD, ARG, or VAR.")

        print(f"Count of {kind} variables: {count}")  # Debugging output
        return count
    def kind_of(self, name: str):
        """Returns the kind of the named identifier, or None if undefined."""
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]["kind"]
        if name in self.class_scope:
            return self.class_scope[name]["kind"]
        return None

    def type_of(self, name: str):
        """Returns the type of the named identifier, or None if undefined."""
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]["type"]
        if name in self.class_scope:
            return self.class_scope[name]["type"]
        return None

    def index_of(self, name: str) -> int:
        """Returns the index assigned to the named identifier, or -1 if undefined."""
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]["index"]
        if name in self.class_scope:
            return self.class_scope[name]["index"]
        return -1

    def define_this_for_method(self) -> None:
        """Defines 'this' as an ARG variable in the current subroutine scope."""
        if not self.current_class_name:
            raise ValueError("Current class name must be set before defining 'this'.")
        self.define("this", self.current_class_name, "ARG")

    def __repr__(self):
        """Debug-friendly representation of the symbol table."""
        return (
            f"Class Scope: {self.class_scope}\n"
            f"Subroutine Scope: {self.subroutine_scope}\n"
            f"Index Counters: {self.index_counters}"
        )
