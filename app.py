from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
import logging


# process_before_response must be True when running on FaaS
app = App(process_before_response=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond_to_slack_within_3_seconds(body, ack):
    text = body.get("text")
    if text is None or len(text) == 0:
        ack(":eyes: Usage: /kot in:出勤 | out:退勤")
    else:
        ack()

import requests
import json
import datetime
import pytz
import os
from airtable import AirtableClientFactory, AirtableSorter, SortDirection
def run_long_process(respond, body, say):

    input_text = body['text']
    #logger.info(body)
    slackid = body['user_id']

    if input_text == "in":
      flag=1
      name = kotPost(flag, slackid)
      logger.info(name)
      say(f":ok: {name}さん :kaisi:")
      
    elif input_text == "out":
      flag=2
      name = kotPost(flag, slackid)
      say(f":ok: {name}さん :syuuryou:")
      
    else:
      url = 'http://checkip.amazonaws.com/'

      res = requests.get(url)
      ip = str(res.text.rstrip('\n'))
      #logger.info(ip)
      respond(f":ng: エラーです {ip}")


app.command("/kot")(
    ack=respond_to_slack_within_3_seconds,  # responsible for calling `ack()`
    lazy=[run_long_process]  # unable to call `ack()` / can have multiple functions
)

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


# king of timeへの打刻処理 code=1:出社, code=2:退社
def kotPost(code, slackid):
  
  employ = getAirTable(slackid)
  url = "https://api.kingtime.jp/v1.0/daily-workings/timerecord/" + employ[0]
  
  kotToken = os.environ['KOT_TOKEN']
  
  headers = {
      'Authorization': "Bearer " + kotToken,
      'content-type': "application/json",
    }

  kotid = getKotId(headers, employ[2])
  logger.info(kotid)
  #url = "https://api.kingtime.jp/v1.0/daily-workings/timerecord/" + kotid
  
  rdatetime = dateGet()
 
  userData = {
      "date": rdatetime[0],
      "time": rdatetime[1],
      "code": code
    }
    
  response = requests.request("POST", url, headers=headers, data=json.dumps(userData))
  logger.info(response.text)
  
  return employ[1]
    
# UTC取得->JST変換->isoformat
def dateGet():
  #日付 2021-02-10
  getdatetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
  currentdate = getdatetime.strftime('%Y-%m-%d')
  #oldcurrentdate = datetime.date.today().strftime('%Y-%m-%d')
  #logger.info(newcurrentdate)
  logger.info(currentdate)

  #時刻 2020-12-29T15:41:52+09:00
  #localtime = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(hours=9)
  #jp = pytz.timezone('Asia/Tokyo') 
  currenttime = getdatetime.replace(microsecond=0).isoformat()
  #oldcurrenttime = jp.localize(localtime).isoformat()
  #logger.info(newcurrenttime)
  logger.info(currenttime)
  
  return currentdate, currenttime

def getAirTable(slackid):
  airtableBaseKey = os.environ['AIRTABLE_BASE_KEY']
  airtableApiKey = os.environ['AIRTABLE_API_KEY']
  
  # ベース毎にファクトリクラスのインスタンスを生成します。
  atf = AirtableClientFactory(base_id=airtableBaseKey, api_key=airtableApiKey)
  
  # テーブル毎にクライアントクラスのインスタンスを生成します。
  at = atf.create('Employee_directory')
  
  # airtableでslackidが合致するレコードを取得する
  atRecord = at.get_by('Slack_id', slackid, view='All_employees')
  a = atRecord.records[0]
  kotid = a['fields']['Kot_id']
  fullname = a['fields']['Firstname'] + '.' + a['fields']['Lastname']
  employeeid = a['fields']['Employee_id']
  #photo = a['fields']['Photo']
  
  #logger.info(employeeid)
  return kotid, fullname, employeeid
  

def getKotId(headers, employeeid):
  userData = {
    "additionalFields": 'currentDateEmployee',
  }
  url = "https://api.kingtime.jp/v1.0/employees"
  response = requests.request("GET", url, headers=headers)

  #print(response.text)
  a = json.loads(response.text)

  for item in a:
    if(item["code"] == employeeid):
      kotid = item["key"]
  
  
  return kotid