# AI log: використовувала для перекладу завдання, пояснення логіки завдання та з опрацюванням помилок
sentence = "The teacher said that That book belongs to her"
words = sentence.lower().split()
counts = {}
for word in words:
    if word in counts:
        counts[word] += 1
    else:
        counts[word] = 1

print(counts)

