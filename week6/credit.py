from cs50 import get_int

type = "INVALID"
card = get_int("Number: ")

# check card type
if (card >= 34 * (10 ** 13) and card < 35 * (10 ** 13)) or (card >= 37 * (10 ** 13) and card < 38 * (10 ** 13)):
    type = "AMEX"
elif card >= 51 * (10 ** 14) and card < 56 * (10 ** 14):
    type = "MASTERCARD"
elif (card >= 4 * (10 ** 12) and card < 5 * (10 ** 12)) or (card >= 4 * (10 ** 15) and card < 5 * (10 ** 15)):
    type = "VISA"

# if card number (without checking with algorithm) is incorrect then exit
if type == "INVALID":
    print("INVALID")
    exit()

sum = 0
even_check = 1

# checking algorithm
while card > 0:
    last_num = card % 10
    if even_check % 2 == 0:
        if last_num * 2 >= 10:
            sum += 1 + ((last_num * 2) % 10)
        else:
            sum += last_num * 2
    else:
        sum += last_num

    even_check += 1
    card = card // 10

# print the answer
if sum % 10 == 0 and type != "INVALID":
    print(f"{type}")
else:
    print("INVALID")