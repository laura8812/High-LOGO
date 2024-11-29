import turtle
def main():
    t = turtle.Turtle()
    s = turtle.Screen()
    s.title('Logo Interpreter')
    t.forward(90)
    t.right(90)
    t.forward(90)
    for _ in range(10):
        t.forward(4)
        t.penup()
        t.forward(4)
turtle.done()
