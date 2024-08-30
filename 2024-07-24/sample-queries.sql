SELECT artists.artist, COUNT(songs.id)
FROM songs
JOIN artists
ON songs.artistID = artists.id
GROUP BY artists.artist
ORDER BY COUNT(songs.id) DESC

-- For each artist, their most used chord
SELECT artists.artist, chord, COUNT(songID)
FROM artists
JOIN songs
ON artists.id = songs.artistID
JOIN join_chord_song
ON songs.id = join_chord_song.songID
JOIN chords
ON join_chord_song.chordID = chords.id
GROUP BY artist, chord
ORDER BY artist, COUNT(songID) DESC

-- Most commonly used tuning?
SELECT LOWER(tuning), COUNT(tuning)
FROM songs
GROUP BY LOWER(tuning)
ORDER BY COUNT(tuning) DESC

SELECT artist, title
FROM songs
JOIN artists
ON songs.artistID = artists.id
WHERE LOWER(tuning) LIKE '%timing is 4/4.'

SELECT COUNT(*)
FROM songs