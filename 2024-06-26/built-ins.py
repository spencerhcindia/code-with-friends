# A function that uses itertools.count and counts from a start arg by 6 until it reaches a target and then returns the number it reaches

from itertools import count, cycle, chain
from random import choices, sample
from collections import defaultdict, Counter, deque

def my_count(start: int, target: int) -> list:
    for i in count(start, 6):
        if i >= target:
            return i

# print(my_count(6, 37))


# A function that prints the letters of the star spangled banner individually using itertools.cycle
# until it has printed k of the letters

banner = """Okay, can you see
By the dawn's early light
What so proudly we hailed
At the twilight's last gleaming?
Whose broad stripes and bright stars
Through the perilous fight
O'er the ramparts we watched
Were so gallantly, yeah, streaming?
And the rockets' red glare
The bombs bursting in air
Gave proof through the night
That our flag was still there
O say, does that star-spangled banner yet wave
O'er the land of the free and the home of the brave"""

def yet_wave(string: str, k: int) -> None:
    count = 0
    for i in cycle(string):
        print(i)
        count += 1
        if count == k:
            break
# yet_wave(banner, 300)

# A function that uses itertools.chain to turn multiple lists
# into one big list containing the elements from each of the lists

def combine(*lists: list) -> list:
    my_list = []
    lists = [element for element in lists if isinstance(element, list)]
    for i in chain(*lists):
        my_list.append(i)
    return list(set(my_list))
# print(combine([1,2,3], ["a","b"], ["butt"], ['p', 'i', 'n', 'u', 's'], [1,2]))

# A function for an int k returns a string of length k that is randomly generated from letters a-z
# and numbers 0-5 using random.choices

def rand_string(k: int) -> str:
    alphabet = 'abcdefghijklmnopqrstuvwxyz012345'
    return "".join(choices(alphabet, k=k))

# print(rand_string(20))

# A function that, given a string, uses random.sample to scramble the str and hand it back to you
# params = return type str

def scramble(string: str) -> str:
    result = "".join(sample(string, len(string)))
    return result

# print(scramble("Mom and Dad are fighting again and it's scaring me more than usual."))

def number_sort(k: int) -> dict:
    shape = defaultdict(list)
    for i in range(k+1):
        if i % 2 == 0:
            shape["even"].append(i)
        if i % 2 != 0:
            shape["odd"].append(i)
        if i % 3 == 0:
            shape["divisible_3"].append(i)
        if i % 5 == 0:
            shape["divisible_5"].append(i)
    return dict(shape)

# print(number_sort(30))

# A function that given a string utilizes collections.counter to return the letter in the string
# with the highest occurrence
#
# if there's a tie it returns none
#
# the following strings:
# hyderabad
# tambourine
# scintillating
# ramparts
# championship

def letter_finder(string: str) -> str | None:

    letters = dict(Counter(string)) # this is a dict with key letter and value num of occurrences

    maximum = max(letters.values()) # this is the highest number of all the values in the above dict

    if dict(Counter(letters.values()))[maximum] > 1:
        return None
    else:
        for element, value in letters.items():
            if value == maximum:
                return element



# print(letter_finder("bamboo"))

# A function that given a string, adds each letter of the string to the deque
# pops them off in the reverse order and thus prints the string in reverse order.

def reverse_string(string: str) -> str:
    my_deque = deque()
    my_stash = ""
    for i in string:
        my_deque.append(i)
        print(my_deque)
    for i in range(len(string)):
        my_stash += my_deque.pop()
        print(my_deque)
    return my_stash

print(reverse_string("mokney kog"))
