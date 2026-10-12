# Task 4

# AI log: Not used

sentence = "Python is fun and python helps me learn coding and Python"

words = {}

for i in sentence.lower().split():
    if i in words:
        words[i] += 1
    else:
        words[i] = 1

print(words)

# {'python': 3, 'is': 1, 'fun': 1, 'and': 2, 'helps': 1, 'me': 1, 'learn': 1, 'coding': 1}
