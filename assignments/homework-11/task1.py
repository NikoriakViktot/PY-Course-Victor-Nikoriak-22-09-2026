# AI log: none

# коли викликається помилка, виконання коду зупиняється, тому коли ми почали ловити KeyError,
# код зупиняється і не доходить до IndexError

#   File "d:\VisualStudioProject\BeetRoot Academy\lesson 11 exeptions\homework-11\task1.py", line 25, in oops
#     print(my_dict['word'])
#           ~~~~~~~^^^^^^^^
# KeyError: 'word'


def oops():

    my_list = []
    my_dict = {}

    print(my_dict['word'])
    print(my_list[0])


def oops2():

    try:
        oops()

    except IndexError as e:
        print(f"Помилка: {e}")


# oops()
oops2()
