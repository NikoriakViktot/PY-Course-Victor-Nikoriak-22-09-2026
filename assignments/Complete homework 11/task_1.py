# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді

def oops ():
  raise IndexError ("помилка! код IndexError")

def call_oops():
    try:
        oops([1, 2, 3])
    except IndexError as e:
        print("Сталася помилка IndexError: ", e)

call_oops()

#Сталася помилка IndexError:  помилка! код IndexError

#def oops (values):
    #raise KeyError ("помилка! код KeyError")

#Програма падає з KeyError, тому що перехоплює лише IndexError