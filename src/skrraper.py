#!/usr/bin/env python
import csv, json, os, traceback, datetime, time, praw, requests, pafy, logging, sys
from BeautifulSoup import BeautifulSoup
from pprint import pprint
from logging.config import dictConfig

logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s:%(name)s:%(levelname)s:%(message)s'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.INFO},
        'fh': {'class': 'logging.FileHandler',
              'formatter': 'f',
              'filename': '../log/skrraper.log',
              'level': logging.INFO}
        },
    root = {
        'handlers': ['fh'],
        'level': logging.INFO,
        }
)

dictConfig(logging_config)
logger = logging.getLogger()

#	Change config to include log file, database, and location to save songs.
#	Create a config object to hold attributes, including reddit_url, reddit_payload, retry_dir, retry_file
def readConfig(env):
	"""
	Read config file
	"""
	if(env == 'd'):
		logger.info('Loading development configuration.')
		with open('../config/dev.conf') as config_file:
			config = json.load(config_file)
	elif(env == 'p'):
		logger.info('Loading production configuration.')
		with open('../config/prod.conf') as config_file:
			config = json.load(config_file)
	return config

def retry(configObject):
	"""
	Retry downloading songs
	Read from file/database for songs that did not download before
	Remove Songs from retry if they were successful
	"""
	#Read from file/database for songs to be retried
	with open(config.retry_dir_file, 'r') as f:
		f.readline()

def parseTitle(submission):
	"""
	Parse submission title
	"""
	return submission.title.split("]",1)[1].split("(",1)[0].strip()

def getSongYoutube(submission):
	"""
	Get Song From Youtube
	Check url of song
	If available, download from Youtube
	"""
	submission_video = None
	if(('youtube' in submission.url) or ('youtu.be' in submission.url)):
		"""
		IOError: ERROR: zx1sEkIi5vg: Youtube says: This video has been removed by the user.
		"""
		try:
			submission_video = pafy.new(submission.url)
		except IOError as err:
			logger.error("IOError error: {0}".format(err))

	else:
		youtube_html	 		= requests.get('https://www.youtube.com/results',params={'search_query': submission.title})
		youtube_content			= BeautifulSoup(youtube_html.content)
		youtube_results			= youtube_content.findAll("a", "yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink      spf-link ")
		if youtube_results:
			submission.url 		= 'https://www.youtube.com'+str(youtube_results[0]['href'])
			submission_video 	= pafy.new(submission.url)
	if(None == submission_video):
		#Add song to retry list/database
		logger.warn('Could not find song: %s', submission.title)
		return
	#Add more checks for valid video
	if((submission_video.length >= 90) and (submission_video.length <= 330)):
		#Send complete message to Slack
		#Add song to database
		submission_audio 		= submission_video.getbestaudio()
		logger.info('Downloaded: %s', str(submission.title.encode('utf-8')))
		submission_audio.download(filepath=config['song']['song_dir'], quiet=True)

def main(config):
	"""
	Main
	Query Reddit
	Create Reddit object from library praw
	Get and download song from Youtube
	"""
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
	"""
	Check needed directories
	Create directories if they are not found
	"""
	#Check for logging directory
	if not os.path.exists(config['retry']['retry_dir']):
		os.makedirs(config['retry']['retry_dir'])
	if not os.path.exists(config['song']['song_dir']):
		os.makedirs(config['song']['song_dir'])

	if not os.path.join(config['retry']['retry_file']):
		f = open(retry_dir_file, 'w')
		f.close()

if(__name__ == "__main__"):
	"""
	Post-Root
	Checks before Main function.
	"""
	if(len(sys.argv) < 2):
		logger.warn('No Environment specified, defaulting to Dev.')
		env		= 'd'
	else:
		env		= sys.argv[1]

	config		= readConfig(env)
	checkDirectories(config)
	main(config)
