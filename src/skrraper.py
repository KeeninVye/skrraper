#!/usr/bin/env python
import csv, json, os, traceback, datetime, time, praw, requests, pafy
from BeautifulSoup import BeautifulSoup
from pprint import pprint

#	Change config to include log file, database, and location to save songs.
#	Create a config object to hold attributes, including reddit_url, reddit_payload, retry_dir, retry_file
def readConfig():
	with open('config/dev.conf') as config_file:
		config = json.load(config_file)
	return config

def retry(configObject):
	with open(config.retry_dir_file, 'r') as f:
		f.readline()

def parseTitle(submission):
	return submission.title.split("]",1)[1].split("(",1)[0].strip()

def getSongYoutube(submission):
	if(('youtube' in submission.url) or ('youtu.be' in submission.url)):
		submission_video = pafy.new(submission.url)
	else:
		youtube_html	 		= requests.get('https://www.youtube.com/results',params={'search_query': submission.title})
		youtube_content			= BeautifulSoup(youtube_html.content)
		youtube_results			= youtube_content.findAll("a", "yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink      spf-link ")
		if youtube_results:
			submission.url 		= 'https://www.youtube.com'+str(youtube_results[0]['href'])
			submission_video 	= pafy.new(submission.url)
	if((submission_video.length >= 90) and (submission_video.length <= 330)):
		submission_audio 		= submission_video.getbestaudio()
		submission_audio.download(filepath='songs/')

def main(config):
	#Query Reddit
	#reddit_songs = getSongsReddit(config)
	reddit = praw.Reddit(client_id=config['client']['client_id'],
					 client_secret=config['client']['client_secret'],
					 user_agent=config['client']['user_agent'])
	subreddit = reddit.subreddit('hiphopheads')
	for submission in subreddit.search('FRESH', sort='new', time_filter='hour', limit=100):
		if(('[FRESH]' in submission.title) or ('[FRESH VIDEO]' in submission.title)):
			submission.title = parseTitle(submission)
			getSongYoutube(submission)
	return

def checkDirectories(config):
	if not os.path.exists(config['retry']['retry_dir']):
		os.makedirs(config['retry']['retry_dir'])

	if not os.path.join(config['retry']['retry_file']):
		f = open(retry_dir_file, 'w')
		f.close()

if(__name__ == "__main__"):
	#Checks before Main function.
	config = readConfig()

	checkDirectories(config)
	main(config)
