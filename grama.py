from lark import Lark
import sys
import subprocess

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

    turtle_command: "FD" num
                   | "BK" num
                   | "RT" num
                   | "LT" num
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
parser = Lark(grammar, start="start", maybe_placeholders=False)

# Generador del archivo Python
def generate_python_file(hlogo_code, output_file):
    def write_line(f, line, indent_level):
        """Escribe una línea en el archivo con la indentación adecuada."""
        f.write(f"{'    ' * indent_level}{line}\n")  # Siempre usa 4 espacios

    with open(output_file, "w") as f:
        f.write("import turtle\n")
        f.write("def main():\n")
        write_line(f, "t = turtle.Turtle()", 1)
        write_line(f, "s = turtle.Screen()", 1)
        write_line(f, "s.title('Logo Interpreter')", 1)

        indent_level = 1
        brace_stack = []

        for line in hlogo_code.splitlines():
            line = line.strip()

            if line.startswith("main"):
                brace_stack.append(indent_level)
                indent_level += 1
            elif line.startswith("if"):
                condition = line[3:].strip(" {")
                write_line(f, f"if {condition}:", indent_level)
                brace_stack.append(indent_level)
                indent_level += 1
            elif line.startswith("while"):
                condition = line[6:].strip(" {")
                write_line(f, f"while {condition}:", indent_level)
                brace_stack.append(indent_level)
                indent_level += 1
            elif line.startswith("REPEAT"):
                times = line.split()[1]
                write_line(f, f"for _ in range({times}):", indent_level)
                brace_stack.append(indent_level)
                indent_level += 1
            elif line == "{":
                continue
            elif line == "}":
                if brace_stack:
                    brace_stack.pop()
                    indent_level -= 1
            elif line.startswith("FD"):
                distance = line.split()[1]
                write_line(f, f"t.forward({distance})", indent_level)
            elif line.startswith("BK"):
                distance = line.split()[1]
                write_line(f, f"t.backward({distance})", indent_level)
            elif line.startswith("RT"):
                angle = line.split()[1]
                write_line(f, f"t.right({angle})", indent_level)
            elif line.startswith("LT"):
                angle = line.split()[1]
                write_line(f, f"t.left({angle})", indent_level)
            elif line == "PU":
                write_line(f, "t.penup()", indent_level)
            elif line == "PD":
                write_line(f, "t.pendown()", indent_level)
            elif line.startswith("WIDTH"):
                width = line.split()[1]
                write_line(f, f"t.width({width})", indent_level)
            else:
                print(f"Comando desconocido: {line}")

        # Usar solo turtle.done() para mantener la ventana abierta
        write_line(f, "turtle.done()", 1)

# Función principal
def main():
    if len(sys.argv) != 2:
        print("Uso: python grama.py <archivo.hlogo>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file + ".py"

    try:
        with open(input_file, "r") as f:
            hlogo_code = f.read()
        generate_python_file(hlogo_code, output_file)
        print(f"Archivo Python generado: {output_file}")

        # Ejecutar el archivo generado usando subprocess
        subprocess.run(["python", output_file], check=True)
    except FileNotFoundError:
        print(f"Error: El archivo {input_file} no existe.")
    except subprocess.CalledProcessError as e:
        print(f"Error durante la ejecución del script generado: {e}")
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__ == "__main__":
    main()
