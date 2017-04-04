#!/usr/bin/env python

import csv, json, spotipy, os, traceback, datetime, requests, BaseHTTPServer
import util
from BeautifulSoup import BeautifulSoup
from pprint import pprint

class Skrraper:
	def __init__(self, user_id, playlist_id, playlist_uris, sp, r_url, r_payload):
		self.user_id 		= user_id
		self.playlist_id 	= playlist_id
		self.playlist_uris	= playlist_uris
		self.sp 			= sp

#	Need to read from config and error out if the values are not there or are not valid.
def read_config():
	with open('config/skrraper.conf') as config_file:
		config = json.load(config_file)
	return config['user']['user_id'], config['user']['username'], config['user']['playlist_id'], config['skrraper']['run_id'], config['skrraper']['client_id'], config['skrraper']['client_secret']

def retry(retry_dir_file):
	with open(self.retry_dir_file, 'r') as f:
		f.readline()

def get_playlist_tracks(playlist_json):
	playlist_tracks = []
	for track in playlist_json['tracks']['items']:
		playlist_tracks.append(track['track']['uri'])
	return playlist_tracks

def main(skrr):

	#Query Reddit
	reddit_response		= requests.get(skrr.reddit_url, skrr.reddit_payload)
	html				= BeautifulSoup(reddit_response.content)
	html_posts			= html.findAll("a", "search-title may-blank")
	print(html_posts)
	print("Starting Loop:")
	for post in html_posts:
		spotify_add = False
		song_uri	= ''
		post_title	= post.string
		link  = post.get('href')
		if("[FRESH]" in post_title):
			song = post_title.split("]",1)[1].split("-",1)
			if(len(song)>1):
				song_artist			= song[0].strip()
				song_title			= song[1].strip()
				spotify_json		= sp.search(q=song_title, type='track')
				#pp.pprint(spotify_json)
				if(spotify_json['tracks']['total'] > 0):
					spotify_tracks = spotify_json['tracks']['items']
					for track in spotify_tracks:
						track_title = track['album']['name'].lower()
						if((track_title == song_title.lower()) and (spotify_add == False)):
							for track_artist in track['album']['artists']:
								if(track_artist['name'].lower() == song_artist.lower()):
									if(not any(track['uri'] in track_uri for track_uri in skrr.playlist_uris)):
										print('Add Song = True')
										spotify_add = True
										song_uri	= track['uri']
										track_id	= track['id']
									else:
										print('Track %s already in playlist.' % song_title)
					if(spotify_add == True):
						sp.user_playlist_add_tracks(skrr.user_id, skrr.playlist_id, [song_uri])
						print("Added "+song_title+" by "+song_artist+" to playlist: "+ skrr.playlist_id)
					else:
						print("Soungs found, but none added for: " + song_title)
				else:
					print("No songs found with title: " + song_title)
		else:
			print("Not Fresh: " + post_title)

if(__name__ == "__main__"):
	user_id, username, playlist_id, run_id, client_id, client_secret = read_config()

	redirect_uri	= 'http://localhost:8888/callback/'
	retry_dir		= 'retry'
	retry_file		= 'retry.log'
	retry_dir_file	= os.path.join(retry_dir, retry_file)

	if(run_id=='TEST'):
		reddit_url		= 'https://www.reddit.com/r/hiphopheads/search'
		reddit_payload	= {'q' : '[FRESH] Chanel', 'restrict_sr' : 'on', 'sort' : 'top', 't' : 'all'}
	else:
		reddit_url		= 'https://www.reddit.com/r/hiphopheads/search'
		reddit_payload	= {'q' : 'FRESH', 'restrict_sr' : 'on', 'sort' : 'top', 't' : 'day'}

	if not os.path.exists(retry_dir):
		os.makedirs(retry_dir)

	if not os.path.join(retry_dir, retry_file):
		f = open(retry_dir_file, 'w')
		f.close()

	#Setup Spotify Object
	scope				= 'playlist-modify-public'
	token				= util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
	sp					= spotipy.Spotify(auth=token)
	playlist_uris		= get_playlist_tracks(sp.user_playlist(user_id, playlist_id=playlist_id))

	skrr = Skrraper(user_id, playlist_id, playlist_uris, sp,reddit_url, reddit_payload)
	main(skrr)