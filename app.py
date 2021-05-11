from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
import logging

app = App(process_before_response=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Slackへのack
def respond_to_slack_within_3_seconds(body, ack):
    #text = body.get("text")
    #logger.info(text)
    #if text is None or len(text) == 0:
    #    ack(":eyes: Usage: /kot in:出勤 | out:退勤")
    #else:
    ack()

import requests
import json
import datetime
import pytz
import os
from airtable import AirtableClientFactory, AirtableSorter, SortDirection
# メイン処理
def run_long_process(respond, body, say):
    ctext = body.get("text")
    logger.info(ctext)
    logger.info(body)
    slackid = body['user_id']
        
    # /kotのとき
    if ctext is None or len(ctext) == 0:
      flag = kotPost(0, slackid)
      
      if flag == "1":
        say(f" <@{slackid}> さん :kaisi:")
      
      elif flag == "2":
        say(f" <@{slackid}> さん :syuuryou:")
        
      else:
        respond(f" :ng: ")

    # /kot breakinのとき
    elif ctext == "breakin":
      flag = kotPost(3, slackid)
      
      if flag == 99:
        respond(f" :ng: codeが99です ")
      else:
        say(f" <@{slackid}> さん :yasumi: :kaisi:")
        
    # /kot breakoutのとき
    elif ctext == "breakout":  
      flag = kotPost(4, slackid)

      if flag == 99:
        respond(f" :ng: codeが99です ")
      else:
        say(f" <@{slackid}> さん :yasumi: :syuuryou:")
        
    else:
      #url = 'http://checkip.amazonaws.com/'
      respond(f":ng: :eyes: Usage: /kot 出勤 & 退勤")

app.command("/kot")(
    ack=respond_to_slack_within_3_seconds,  # responsible for calling `ack()`
    lazy=[run_long_process]  # unable to call `ack()` / can have multiple functions
)

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)

# king of timeへの打刻処理 code=0:自動打刻, code=3:休憩開始, code=4:休憩終了
def kotPost(code, slackid):
  
  kotid = getAirTable(slackid)
  url = "https://api.kingtime.jp/v1.0/daily-workings/timerecord/" + kotid  
  kotToken = os.environ['KOT_TOKEN']
  headers = {
      'Authorization': "Bearer " + kotToken,
      'content-type': "application/json",
    }

  rdatetime = dateGet()
  logger.info(rdatetime)
  
  # code=0:自動打刻
  if code == 0:
    userData = {
        "date": rdatetime[0],
        "time": rdatetime[1],
    }
  # code=3:休憩開始, code=4:休憩終了
  elif code == 3 or code == 4:
    userData = {
        "date": rdatetime[0],
        "time": rdatetime[1],
        "code": code
    }
  else:
    return 99
  logger.info(code)
  response = requests.request("POST", url, headers=headers, data=json.dumps(userData))
  restext = json.loads(response.text)
  _rcode = restext['timeRecord']['code']
  
  return _rcode

# AirTableからKing of TimeのIDを取得する
def getAirTable(slackid):
  airtableBaseKey = os.environ['AIRTABLE_BASE_KEY']
  airtableApiKey = os.environ['AIRTABLE_API_KEY']
  
  atf = AirtableClientFactory(base_id=airtableBaseKey, api_key=airtableApiKey)
  at = atf.create('Employee_directory')
  
  # airtableでslackidが合致するレコードを取得する
  atRecord = at.get_by('Slack_id', slackid, view='All_employees')
  a = atRecord.records[0]
  _rkotid = a['fields']['Kot_id']
  
  return _rkotid

# UTC取得->JST変換->isoformat
def dateGet():
  #日付 2021-02-10
  getdatetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
  currentdate = getdatetime.strftime('%Y-%m-%d')

  #時刻 2020-12-29T15:41:52+09:00
  currenttime = getdatetime.replace(microsecond=0).isoformat()
  
  return currentdate, currenttime

