from cs50 import get_int

# height prompt
while True:
    height = get_int("Height: ")
    if height >= 1 and height <= 8:
        break

# "drawing" pyramids
for i in range(1, height + 1):
    for j in range((height - i)):
        print(" ", end="")
    for j in range(i):
        print("#", end="")
    print("  ", end="")
    for j in range(i):
        print("#", end="")
    print()