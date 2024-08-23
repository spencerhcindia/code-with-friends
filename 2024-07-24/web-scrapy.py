from pydoc import cli
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import sqlite3
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import re
from selenium.webdriver.chrome.options import Options
from pprint import pprint



DB_FILENAME = "song_data.db"

con = sqlite3.connect(DB_FILENAME)
cur = con.cursor()

# cur.execute("INSERT INTO songs (title, artist, tuning, chords) VALUES (...)")

def init_db_schema():
    cur.execute("CREATE TABLE artists(id integer PRIMARY KEY, artist text UNIQUE)")
    cur.execute("CREATE TABLE songs(id integer PRIMARY KEY, artistID integer, title text, tuning text)")
    cur.execute("CREATE TABLE chords(id integer PRIMARY KEY, chord text UNIQUE)")
    cur.execute("CREATE TABLE join_chord_song(chordID integer, songID integer)")
    cur.execute("CREATE TABLE scraped_pages(href UNIQUE NOT NULL)")
    con.commit()

def db_schema_is_ready(table_names):
    # For every table we expect to exist, we verify that it exists in sqlite master
    # If any of the tables don't exist, we return false immediately; otherwise we return true

    for i in table_names:
        if not cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{i}';").fetchone():
            return False
    return True

def drop_tables(table_names):
    for i in table_names:
        if cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{i}';").fetchone():
            cur.execute(f"DROP TABLE {i}")
    con.commit()


def init_db():
    # If a .db file exists try to connect to it;
    # Otherwise, we need to create a new db file and run init_db_schema
    # Because this means our db does not yet exist
    tables = ("artists", "songs", "chords", "join_chord_song")
    if not db_schema_is_ready(tables):
        drop_tables(tables)
        init_db_schema()


init_db()


def insert_artist(artist:str):
    id = cur.execute(f"""
                INSERT INTO artists (artist) VALUES (?)
                ON CONFLICT do nothing
                RETURNING id;
                """, (artist,)).fetchone()
    if id is None:
        id = cur.execute("SELECT id FROM artists WHERE artist=(?)", (artist,)).fetchone()

    con.commit()
    return id[0]

def insert_song(artistID:int, title:str, tuning:str):
    id = cur.execute(f"""
                INSERT INTO songs (artistID, title, tuning) VALUES (?, ?, ?)
                RETURNING id;
                """, (str(artistID), str(title), str(tuning))).fetchone()
    con.commit()
    return id[0]

def insert_chord(chord:str):
    id = cur.execute(f"""
                INSERT INTO chords (chord) VALUES (?)
                ON CONFLICT do nothing
                RETURNING id;
                """, (chord,)).fetchone()
    if id is None:
        id = cur.execute("SELECT id FROM chords WHERE chord=(?)", (chord,)).fetchone()
    con.commit()
    return id[0]

def insert_join(chordID:int, songID:int):
    cur.execute(f"""
                INSERT INTO join_chord_song (chordID, songID)
                VALUES (?, ?);
                """, (str(chordID), str(songID)))
    con.commit()

def insert_song_data(artist:str, title:str, tuning:str, chords:tuple):
    artistID = insert_artist(artist=artist)
    songID = insert_song(artistID=artistID, title=title, tuning=tuning)
    for i in chords:
        chordID = insert_chord(chord=i)
        insert_join(songID=songID, chordID=chordID)

def get_all_scraped_pages() -> set[str]:
    return {href[0] for href in cur.execute(f"SELECT href FROM scraped_pages").fetchall()}

def add_scraped_page(href):
    cur.execute("INSERT INTO scraped_pages (href) VALUES (?)", (str(href),))
    con.commit()

def analysis_chord_counts():
    sql = """
            SELECT chord, COUNT(songID)
            FROM join_chord_song
            JOIN chords ON join_chord_song.chordID = chords.id
            GROUP BY chordID
            ORDER BY 2 DESC
            """
    return [{"chord": chord, "count": count} for (chord, count) in cur.execute(sql).fetchall()]


previously_scraped_pages = get_all_scraped_pages()


chromedriver_autoinstaller.install()

options = Options()
options.set_capability("pageLoadStrategy", "eager")

# Dis my driver, it drives the browser.
driver = webdriver.Chrome(options=options)
driver.get("https://www.guitartabs.cc/tabs/0-9/")

# Dis my actions, it allows me to interact with the webpage.
actions = ActionChains(driver)
link = driver.find_element(By.XPATH, "//*[@id='main_content']/table[1]/tbody/tr/td[2]/div[2]/div/div/div/a[1]").click()


def click_safe(element):
    """
    This function takes an argument of a web element, tries to click it, and returns a boolean depending on the outcome of the click.
    """
    try:
        element.click()
        driver.implicitly_wait(3)
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
        tuning_string = ""
        if tuning_match and tuning_match.group("tuning"):
            print("Tuning: ", tuning_match.group("tuning"))
            tuning_string = tuning_match.group("tuning")

        insert_song_data(artist=artist_name, title=song_title, tuning=tuning_string, chords=chord_strings)

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
            href = song_element.get_attribute('href')
            if href in previously_scraped_pages:
                print("Skipping this href, already scanned: ", href)
                continue
            #And if we can load it
            if not click_safe(song_element):
                continue
            # We find the checkbox to show the chords to the song
            checkbox_xpath = '//*[@id="showing_chords_down"]'
            checkbox = find_xpath_safe(checkbox_xpath)

            # And click it
            if checkbox and click_safe(checkbox):

                # Gather all the details
                find_song_details()

            add_scraped_page(href=href)

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
            artist_href = artist_element.get_attribute('href')
            if artist_href in previously_scraped_pages:
                print("Artist completed, skipping: ", artist_href)
                continue
            # We load it
            if click_safe(artist_element):
                # And attempt to load each of their songs
                scrape_artist_songs()
                # When we are done with this artist, we navigate back and continue.
                driver.back()
                add_scraped_page(artist_href)

        if i % 5 == 0:
            print(f"{i} artists scraped, analysis:")
            pprint(analysis_chord_counts())
            print()




scrape_artists()
