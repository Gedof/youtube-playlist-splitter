from math import ceil
import os
import re

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube"]

def get_youtube_api():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)

    credentials = flow.run_local_server(host='localhost',
      port=8080, 
      authorization_prompt_message='Please visit this URL: {url}', 
      success_message='The auth flow is complete; you may close this window.',
      open_browser=True)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube

def get_playlist_videos(youtube_api, playlist_id:str) -> list:
    next_page_token = None
    video_ids = []

    while True:
        request = youtube_api.playlistItems().list(
            part="snippet",
            maxResults=50,
            playlistId=playlist_id,
            pageToken=next_page_token
        )
        response = request.execute()

        next_page_token = response.get('nextPageToken')
        video_ids.extend([item['snippet']['resourceId']['videoId'] for item in response['items']])

        if next_page_token == None:
            break
    
    return video_ids

def get_playlists(youtube_api, playlist_title:str) -> list:
    next_page_token = None
    playlists = []

    while True:
        request = youtube_api.playlists().list(
            part="snippet",
            maxResults=50,
            mine=True,
            pageToken=next_page_token
        )
        response = request.execute()

        regex = playlist_title + r" \(\d+\/\d+\)"

        next_page_token = response.get('nextPageToken')
        playlists.extend([
            {'id': item['id'], 'title': item['snippet']['title']} 
            for item 
            in response['items'] 
            if re.search(regex, item['snippet']['title'])
        ])

        if next_page_token == None:
            break
    
    return playlists

def insert_playlist(youtube_api, playlist_title:str) -> str:
    request = youtube_api.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": playlist_title
          },
          "status": {
            "privacyStatus": "unlisted"
          }
        }
    )

    return request.execute()['id']

def get_playlist_items(youtube_api, playlist_id:str) -> list:
    next_page_token = None
    item_ids = []

    while True:
        request = youtube_api.playlistItems().list(
            part="snippet",
            maxResults=50,
            playlistId=playlist_id,
            pageToken=next_page_token
        )
        response = request.execute()

        next_page_token = response.get('nextPageToken')
        item_ids.extend([{'id': item['id'], 'video': item['snippet']['resourceId']['videoId']} for item in response['items']])

        if next_page_token == None:
            break
    
    return item_ids

def clear_playlist(youtube_api, playlist_id:str, ex_videos:list = {}):
    items = get_playlist_items(youtube_api, playlist_id)
    items = filter(lambda x: x['video'] not in ex_videos, items)

    for item in items:
        request = youtube_api.playlistItems().delete(
            id = item['id']
        )
        request.execute()

def insert_playlist_videos(youtube_api, playlist_id:str, video_ids:list):
    current_videos = get_playlist_videos(youtube_api, playlist_id)
    video_ids = filter(lambda x: x not in current_videos, video_ids)

    for id in video_ids:
        request = youtube_api.playlistItems().insert(
            part="snippet",
            body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                "kind": "youtube#video",
                "videoId": id
                }
            }
            }
        )
        try:
            response = request.execute()
        except:
            continue

def split_playlist(youtube_api, playlist_id:str, playlist_title:str, max_videos:int) -> list:
    video_ids = get_playlist_videos(youtube_api, playlist_id)
    max_list = ceil(len(video_ids) / max_videos)
    split_lists = []

    for i in range(0, max_list):
        start = max_videos*i
        end = start + max_videos
        split_videos = video_ids[start:end]
        split_title = f"{playlist_title} ({i+1}/{max_list})"
        split_lists.append({'title': split_title, 'videos': split_videos})
    
    return split_lists

def delete_split_playlist(youtube_api, playlists, max_list):
    for plist in playlists:
        regex = r'\(\d+\/(?P<max>\d+)\)'
        match = re.search(regex, plist['title'])
        if int(match['max']) > max_list:
            youtube_api.playlists().delete(
                id = plist['id']
            ).execute()

def update_playlist_title(youtube_api, playlist_id, title):
    youtube_api.playlists().update(
                part="snippet",
                body={
                    "id": playlist_id,
                    "snippet": {
                        "title": title
                    }
                }
            ).execute()

def update_split_playlist(youtube_api, split_playlist, playlists):
    regex = r'\((?P<page>\d+)\/\d+\)'
    playlist_page = re.search(regex, split_playlist['title'])['page']
    duplicate = next((x for x in playlists if re.search(regex, x['title'])['page'] == playlist_page), None)

    if duplicate == None:
        playlist_id = insert_playlist(youtube_api, split_playlist['title'])
    else:
        playlist_id = duplicate['id']
        if duplicate['title'] != split_playlist['title']:
            update_playlist_title(youtube_api, playlist_id, split_playlist['title'])


    clear_playlist(youtube_api, playlist_id, split_playlist['videos'])
    insert_playlist_videos(youtube_api, playlist_id, split_playlist['videos'])