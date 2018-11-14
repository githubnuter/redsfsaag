import httplib2
import os
import sys
import argparse

from random import randint
from time import sleep

from googleapiclient.discovery import build_from_document, build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = "AIzaSyDgQlPIPFhRcudvCMZfODS2ukYXo9uFW2s"
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))



def search():
  info = open(os.path.join(os.path.dirname(__file__), 'search.txt')).read().split('\n')
  return info[randint(0,len(info) - 1)]
def messages():
  info = open(os.path.join(os.path.dirname(__file__), 'messages.txt')).read().split('\n')
  return info[randint(0,len(info) - 1)]

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(os.path.join(os.path.dirname(__file__),CLIENT_SECRETS_FILE), scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  with open(os.path.join(os.path.dirname(__file__),'youtube-v3-discoverydocument.json'), "r", encoding="utf8") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

def insert_comment(youtube, channel_id, video_id, text):
  insert_result = youtube.commentThreads().insert(
    part="snippet",
    body=dict(
      snippet=dict(
        channelId=channel_id,
        videoId=video_id,
        topLevelComment=dict(
          snippet=dict(
            textOriginal=text
          )
        )
      )
    )
  ).execute()

  comment = insert_result["snippet"]["topLevelComment"]
  text = comment["snippet"]["textDisplay"]

  print('Sended text: ' + text)

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  search_response = youtube.search().list(
    q=options.q,
    part="id,snippet",
    maxResults=options.max_results
  ).execute()

  videos = []

  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos.append('%s \n %s' % (search_result["id"]["videoId"],
                                  search_result["snippet"]["channelId"]))

  return videos

if __name__ == "__main__":
  count = 0
  while True:
    argparser = argparse.ArgumentParser(conflict_handler='resolve')
    argparser.add_argument("--q", default=search())
    argparser.add_argument("--max-results", default=50)
    args = argparser.parse_args()
    try:
      videos = youtube_search(args)
    except:
      pass
    for x in videos:
      x = x.split('\n')
      argparser = argparse.ArgumentParser(conflict_handler='resolve')
      argparser.add_argument('--auth_host_name', default='localhost')
      argparser.add_argument('--noauth_local_webserver', action='store_true', default=False)
      argparser.add_argument('--auth_host_port', default=[8080, 8090], type=int, nargs='*')
      argparser.add_argument('--logging_level', default='ERROR', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
      argparser.add_argument("--channelid", default=x[1])
      argparser.add_argument("--videoid", default=x[0])
      argparser.add_argument("--text", default=messages())
      args = argparser.parse_args()
      youtube = get_authenticated_service(args)
      try:
        insert_comment(youtube, args.channelid, args.videoid, args.text)
      except:
        print('Error')
      count+= 1
      print('Sended {0} message, videoid: {1}'.format(count, x[0]))
      sleep(3)
    sleep(1800)
