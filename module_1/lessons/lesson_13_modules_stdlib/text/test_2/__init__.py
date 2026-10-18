import math
print("__file__:", __file__)
print("__name__:", __name__)

print(math.sin(math.pi/2))
print(math.e)





import turtle

# Налаштування екрана
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Infinite Turtle Spiral")

# Налаштування черепашки
t = turtle.Turtle()
t.speed(0)
t.shape("turtle")

colors = ["red", "purple", "blue", "green", "orange", "yellow"]

x = 0

def draw():
    global x

    try:
        t.pencolor(colors[x % 6])
        t.width(x // 100 + 1)
        t.forward(x)
        t.left(59)

        x += 1

        # Після 300 кроків починаємо заново
        if x >= 300:
            x = 0
            t.clear()
            t.penup()
            t.home()
            t.pendown()

        # Наступний крок через __ мс
        screen.ontimer(draw, 1)

    except turtle.Terminator:
        return

# Запускаємо анімацію
draw()

# Головний цикл вікна
screen.mainloop()
