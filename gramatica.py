from lark import Lark, Transformer, v_args
import turtle
import sys
import os

# Definición de la gramática
grammar = r"""
    start: statement*

    statement: loop
             | repeat
             | command
             | if_statement
             | while_statement
             | function_definition
             | function_call
             | main_statement

    loop: "for" identifier "in" "range" "(" num ("," num)* ")" "{" statement* "}"

    repeat: "REPEAT" num "{" statement* "}"

    if_statement: "if" condition "{" statement* "}"

    while_statement: "while" condition "{" statement* "}"

    function_definition: "def" identifier "(" (identifier ("," identifier)*)? ")" "{" statement* "}"

    function_call: identifier "(" (expr ("," expr)*)? ")"

    main_statement: "main" "{" statement* "}"

    command: turtle_command
            | "WIDTH" num

    turtle_command: "FD" num | CNAME
                   | "BK" num | CNAME
                   | "RT" num | CNAME
                   | "LT" num | CNAME
                   | "PU"
                   | "PD"

    condition: expr (logical_op expr)*

    logical_op: "and" | "or" | "<" | ">" | "==" | "!=" | ">=" | "<="

    expr: CNAME
         | num
         | "!" expr
         | expr arithmetic_op expr

    arithmetic_op: "+" | "-" | "*" | "/" | "%"

    identifier: CNAME
    num: SIGNED_NUMBER

    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""

# Configuración del parser
parser = Lark(grammar, start='start', maybe_placeholders=False)

# Clase del intérprete
class LogoInterpreter(Transformer):
    def __init__(self):
        self.variables = {}
        self.turtle = turtle.Turtle()
        self.screen = turtle.Screen()
        self.screen.title("Logo Interpreter")
        self.pen_is_up = False  # Estado de la pluma, empieza levantada

    def start(self, items):
        for item in items:
            if item:
                item

    def for_loop(self, items):
        var = items[0]
        range_args = items[1:-1]
        body = items[-1]
        if len(range_args) == 1:
            start = 0
            end = int(range_args[0])
            step = 1
        elif len(range_args) == 2:
            start = int(range_args[0])
            end = int(range_args[1])
            step = 1
        elif len(range_args) == 3:
            start = int(range_args[0])
            end = int(range_args[1])
            step = int(range_args[2])
        else:
            return
        for value in range(start, end, step):
            self.variables[var] = value
            for stmt in body:
                stmt

    def repeat(self, items):
        repeat_count = int(items[0])
        body = items[1:]
        for _ in range(repeat_count):
            for stmt in body:
                stmt

    def turtle_command_fd(self, items):
        distance = int(items[0])
        if self.pen_is_up:
            self.turtle.pendown()  # Baja la pluma si está levantada
            self.pen_is_up = False
        self.turtle.forward(distance)  # Avanza dibujando

    def turtle_command_bk(self, items):
        distance = int(items[0])
        if self.pen_is_up:
            self.turtle.pendown()  # Baja la pluma si está levantada
            self.pen_is_up = False
        self.turtle.backward(distance)  # Retrocede dibujando

    def turtle_command_rt(self, items):
        angle = int(items[0])
        self.turtle.right(angle)

    def turtle_command_lt(self, items):
        angle = int(items[0])
        self.turtle.left(angle)

    def turtle_command_pu(self, items):
        self.turtle.penup()  # Levanta la pluma
        self.pen_is_up = True

    def turtle_command_pd(self, items):
        self.turtle.pendown()  # Baja la pluma
        self.pen_is_up = False

    def command_width(self, items):
        width = int(items[0])
        self.turtle.width(width)

    def command_other(self, items):
        # En caso de ser necesario
        pass

    def variable_assignment(self, items):
        var = items[1]
        value = self.evaluate_expression(items[3])
        self.variables[var] = value

    def evaluate_condition(self, items):
        if len(items) == 1:
            return self.evaluate_expression(items[0])
        else:
            left = self.evaluate_expression(items[0])
            op = items[1]
            right = self.evaluate_expression(items[2])
            if op == 'and':
                return left and right
            elif op == 'or':
                return left or right
            elif op == '<':
                return left < right
            elif op == '>':
                return left > right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '>=':
                return left >= right
            elif op == '<=':
                return left <= right

    def evaluate_expression(self, items):
        if isinstance(items, list):
            if len(items) == 1:
                return self.evaluate_expression(items[0])
            elif len(items) == 2 and items[0] == '!':
                return not self.evaluate_expression(items[1])
            elif len(items) == 3:
                left = self.evaluate_expression(items[0])
                op = items[1]
                right = self.evaluate_expression(items[2])
                if op == '+':
                    return left + right
                elif op == '-':
                    return left - right
                elif op == '*':
                    return left * right
                elif op == '/':
                    return left / right
                elif op == '%':
                    return left % right
        else:
            if isinstance(items, int):
                return items
            elif isinstance(items, str):
                if items in self.variables:
                    return self.variables[items]
                else:
                    return items
            else:
                return items

# Función para ejecutar el intérprete
def run_logo_interpreter(code):
    interpreter = LogoInterpreter()
    parse_tree = parser.parse(code)
    interpreter.transform(parse_tree)
    turtle.done()

# Función para generar el archivo .py
def generate_python_file(hlogo_code, output_file):
    with open(output_file, 'w') as f:
        f.write("import turtle\n")
        f.write("t = turtle.Turtle()\n")
        f.write("s = turtle.Screen()\n")
        f.write("s.title('Logo Interpreter')\n")
        indent_level = 0

        for line in hlogo_code.splitlines():
            line = line.strip()
            if line.startswith("for"):
                var, range_args = line.split()[1], line.split('(')[1].split(')')[0].split(',')
                f.write(f"for {var} in range({','.join(range_args)}):\n")
                indent_level += 1
            elif line.startswith("REPEAT"):
                repeat_count = line.split()[1]
                f.write(f"{'    ' * indent_level}for _ in range({repeat_count}):\n")
                indent_level += 1
            elif line.startswith("{"):
                pass
            elif line.startswith("}"):
                indent_level -= 1
            else:
                if line.startswith("FD"):
                    distance = line.split()[1]
                    f.write(f"{'    ' * indent_level}t.forward({distance})\n")
                elif line.startswith("BK"):
                    distance = line.split()[1]
                    f.write(f"{'    ' * indent_level}t.backward({distance})\n")
                elif line.startswith("RT"):
                    angle = line.split()[1]
                    f.write(f"{'    ' * indent_level}t.right({angle})\n")
                elif line.startswith("LT"):
                    angle = line.split()[1]
                    f.write(f"{'    ' * indent_level}t.left({angle})\n")
                elif line.startswith("PU"):
                    f.write(f"{'    ' * indent_level}t.penup()\n")
                elif line.startswith("PD"):
                    f.write(f"{'    ' * indent_level}t.pendown()\n")
                elif line.startswith("WIDTH"):
                    width = line.split()[1]
                    f.write(f"{'    ' * indent_level}t.width({width})\n")
                elif line.startswith("SET"):
                    var, value = line.split()[1], line.split()[3]
                    f.write(f"{'    ' * indent_level}{var} = {value}\n")
        f.write("turtle.done()\n")

# Función principal
def main():
    if len(sys.argv) != 2:
        print("Uso: python grama.py <archivo.hlogo>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file + ".py"

    with open(input_file, 'r') as f:
        hlogo_code = f.read()

    generate_python_file(hlogo_code, output_file)
    os.system(f"python {output_file}")

if __name__ == "__main__":
    main()