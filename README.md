# youtube-playlist-splitter

Add an OAuth 2.0 file called "client_secret.json" to project root with API credentials.

```
usage: PlaylistSplitter.py [-h] --playlist_id PLAYLIST_ID --playlist_title PLAYLIST_TITLE --videos VIDEOS

optional arguments:
  -h, --help            show this help message and exit
  --playlist_id PLAYLIST_ID, -id PLAYLIST_ID
                        Id of the playlist to split. (Required)
  --playlist_title PLAYLIST_TITLE, -t PLAYLIST_TITLE
                        Base title of the resulting playlists. (Required)
  --videos VIDEOS, -v VIDEOS
                        Max number of videos per resulting playlist. (Required)
```
