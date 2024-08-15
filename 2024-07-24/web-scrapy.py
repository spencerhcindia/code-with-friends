from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import sqlite3
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import re


con = sqlite3.connect("song_data.db")
cur = con.cursor()

cur.execute("INSERT INTO songs (title, artist, album, tuning, capo) VALUES ('gravity', 'john mayer', 'gravity', 'standard', 0)")
cur.execute("INSERT INTO songs (title, artist, album, tuning, capo) VALUES ('weenis', 'asava', 'ep', 'not standard', 0)")


chromedriver_autoinstaller.install()

driver = webdriver.Chrome()
driver.get("https://www.guitartabs.cc/tabs/0-9/")


actions = ActionChains(driver)
link = driver.find_element(By.XPATH, "//*[@id='main_content']/table[1]/tbody/tr/td[2]/div[2]/div/div/div/a[1]").click()

def click_safe(element):
    """
    This function takes an argument of a web element, tries to click it, and returns a boolean depending on the outcome of the click.
    """
    try:
        element.click()
        return True
    except (NoSuchElementException, ElementClickInterceptedException):
        return False

def chords_valid(chords: List[str]) -> bool:
    """
    This function takes an arg of a list of strings that are then looped thru and validated by checking if
    they start with an actual chord letter, and returns True when it is a valid chord
    """
    for i in chords:
        if not i.lower().startswith(("a", "b", "c", "d", "e", "f", "g")):
            return False
    return True

tuning_pattern = re.compile(r"Tuning\:?\s?(?P<tuning>.*)?$", re.MULTILINE)

def find_song_details():
    """
    This function can run when you are on a page of a song itself
    It attempts to get to artist name, song title, tuning, and chords
    When it's done it prints the song details that were found (or not found)
    """

    # Find the artist name towards top right of page, get the text and strip the suffix off the end
    artist_name = driver.find_element(By.XPATH, "//*[@id='main_content']/table[2]/tbody/tr[1]/td[2]/div/a[3]").text.removesuffix(" tabs")

    # Find the song name towards top right of page, get the text and strip the suffix off the end
    song_title = driver.find_element(By.XPATH, "//*[@id='main_content']/table[2]/tbody/tr[1]/td[2]/div/a[4]").text.removesuffix(" Chords")

    # Find the chords by checking the popup box, each chord is held in a td element
    chords = driver.find_elements(By.XPATH, "//*[@class='crd']/center")

    # Chords is a list of Webelements. We need to transform into strings so we can validate and manipulate them.
    chord_strings = [x.text for x in chords]

    # We need to ensure that the chords are actual chords: for example "h" is not a chord, but appeared in an edge case i happened upon
    if chords_valid(chord_strings):
        # Let's print the data we've collected so far
        print("Artist Name: " + artist_name)
        print("Song Title: " + song_title)
        print("Chords: ")
        print(chord_strings)

        # Here we get the text body that contains the Tuning of the song, unfortunately it is the entire boday of the page.
        tuning = driver.find_element(By.XPATH, "//*[@id='main_content']/table[2]/tbody/tr[2]/td[2]/div[2]/div[2]/div/div[4]/font/pre")

        # We are using tuning_pattern (a regex statement) to parse out the tuning from the tuning element we grabbed
        tuning_match = tuning_pattern.search(tuning.text)

        # If we find the tuning on the page, we print it, otherwise we skip
        if tuning_match and tuning_match.group("tuning"):
            print("Tuning: ", tuning_match.group("tuning"))

    # This else indicated there was bad data in this song (invalid chords) and dismisses that entry
    else:
        print("Song is pooched: ", song_title)

    print()
    print()

def find_xpath_safe(xpath):
    """
    This function takes an arg of an xpath (str) and attempts to find it on the page.
    If it finds the element it returns the element, otherwise handles exception by returning None
    """
    try:
        return driver.find_element(By.XPATH, xpath)

    except NoSuchElementException:

        return None

def scrape_artist_songs():
    """
    This function takes place on a page of an artist's songs
    It loops thru each element, which is a song, on the page and attempts to load on it
    If it loads a song, it clicks a checkbox that opens a dialogue box that contains the chords for that song
    It then attempts to gather the song's details before navigating back and moving on to the next song
    """

    # This captures how many songs are on this specific page
    table_row_count = len(driver.find_elements(By.XPATH, "//*[@id='main_content']/table[2]/tbody/tr[2]/td[2]/div[2]/div[2]/table/tbody/tr[*]"))

    # For every song
    for i in range(2, table_row_count + 1):
        # Attempt to get the link for this song
        song_xpath = f"//*[@id='main_content']/table[2]/tbody/tr[2]/td[2]/div[2]/div[2]/table/tbody/tr[{i}]/td[2]/a"
        song_element = find_xpath_safe(song_xpath)

        # If we find it
        if song_element:
            #And if we can load it
            if not click_safe(song_element):
                continue
            # We find the checkbox to show the chords to the song
            checkbox_xpath = '//*[@id="showing_chords_down"]'
            checkbox = find_xpath_safe(checkbox_xpath)

            # And click it
            if checkbox and click_safe(checkbox):
                print("Checkbox clicked ;D")

                # Gather all the details
                find_song_details()

            # Navigate back and continue
            driver.back()


def scrape_artists():
    """
    This function takes place on a page with a list of artists
    It attempts to load each of them
    """

    # This captures how many artists are on this specific page
    table_row_count = len(driver.find_elements(By.XPATH, "//*[@id='main_content']/table[2]/tbody/tr[2]/td[2]/div[2]/div[2]/table/tbody/tr[*]"))

    # For every artist
    for i in range(2, table_row_count + 1):

        # Get the link to their songs
        artist_xpath = f"//*[@id='main_content']/table[2]/tbody/tr[2]/td[2]/div[2]/div[2]/table/tbody/tr[{i}]/td[2]/a"
        artist_element = find_xpath_safe(artist_xpath)

        # And if we find it
        if artist_element:

            # We load it
            artist_element.click()

            # And attempt to load each of their songs
            scrape_artist_songs()

            # When we are done with this artist, we navigate back and continue.
            driver.back()

scrape_artists()
