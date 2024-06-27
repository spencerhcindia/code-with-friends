# A function that uses itertools.count and counts from a start arg by 6 until it reaches a target and then returns the number it reaches

from itertools import count, cycle, chain

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
print(combine([1,2,3], ["a","b"], ["butt"], ['p', 'i', 'n', 'u', 's'], [1,2]))
