import argparse
import textwrap
import playlist_functions as pf


class ArgumentDefaultsHelpFormatter(argparse.RawTextHelpFormatter):
    def _get_help_string(self, action):
        return textwrap.dedent(action.help)

def start():
    parser = argparse.ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--playlist_id', '-id', required=True, help='Id of the playlist to split. (Required)')
    parser.add_argument('--playlist_title', '-t', required=True, help='Base title of the resulting playlists. (Required)')
    parser.add_argument('--videos', '-v', type=int, required=True, help='Max number of videos per resulting playlist. (Required)')
    
    args = parser.parse_args()

    playlist_id = args.playlist_id
    playlist_title = args.playlist_title
    max_videos = args.videos

    youtube_api = pf.get_youtube_api()
    split_playlists = pf.split_playlist(youtube_api, playlist_id, playlist_title, max_videos)
    current_playlists = pf.get_playlists(youtube_api, playlist_title)
    
    for plist in split_playlists:
        pf.update_split_playlist(youtube_api, plist, current_playlists)

    pf.delete_split_playlist(youtube_api, current_playlists, len(split_playlists))

if __name__ == '__main__':
    start()