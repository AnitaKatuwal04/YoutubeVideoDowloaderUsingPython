import csv
import os
from pytube import YouTube
from googleapiclient.discovery import build
import requests
import  pandas as pd
import numpy as np

api_key='AIzaSyAJjGyRZbHfuTViEKF_IMpksNHBXHzGZRU'
channel_id = 'UC68LOl1l1oLTgW22hQDcduA' #can pass channel id of multiple channels as a form of list

youtube=build('youtube','v3',developerKey=api_key)

def channel_status(youtube, channel_id):
    request=youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id
    )
    response=request.execute()
    datas=dict(Channel_name=response['items'][0]['snippet']['title'],
              Views=response['items'][0]['statistics']['viewCount'],
              Subscribers=response['items'][0]['statistics']['subscriberCount'],
              Playlist_id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
    return datas

def save_status_to_csv(datas, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Channel Name', 'Views', 'Subscribers','Playlist'])  # header row
        csv_writer.writerow([datas['Channel_name'], datas['Views'], datas['Subscribers'],datas['Playlist_id']])
        
        for data in datas:
            csv_writer.writerow([data])
            
#functions to get video ids
def get_video_id(youtube, Playlist_id):
    request=youtube.playlistItems().list(
        part='contentDetails',
        playlistId=Playlist_id,
        maxResults=50
    )
    response=request.execute()
    video_ids=[]
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])

    next_page_token=response.get('nextPageToken')
    more_pages=True
    
    while more_pages:
        if next_page_token is None:
            more_pages=False
        else:
            request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=Playlist_id,
            maxResults=50,
            pageToken=next_page_token)
            
            response=request.execute()
            
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])  
        
    next_page_token=response.get('nextPageToken')
    
    return video_ids

def save_ids_to_csv(video_ids, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['VideoIDS'])  # header row
        csv_writer.writerow([video_ids])
        
        for video_id in video_ids:
            csv_writer.writerow([video_id])

def download_video(video_id):
    youtube = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    video = youtube.streams.get_highest_resolution()
    video.download()
    
def main():
    # Get channel status and save to CSV
    channel_status_data = channel_status(youtube, channel_id)
    save_status_to_csv(channel_status_data, 'channel_status.csv')

    # Get video IDs from channel playlist and save to CSV
    video_ids = get_video_id(youtube, channel_status_data['Playlist_id'])
    save_ids_to_csv(video_ids, 'video_ids.csv')

    # Download the first video from the list of video IDs
    download_video(video_ids[0])

if __name__ == '__main__':
    main()