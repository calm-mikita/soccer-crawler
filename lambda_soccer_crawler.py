import telegram
import os
import dotenv
import certifi
import urllib3
import json
import boto3
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

#telegram bot setup
dotenv.load_dotenv(os.path.join(os.getcwd(), "component\.env"))
my_token = os.getenv("TELEGRAM_BOT_TOKEN")
my_chat = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=my_token)

#s3 setup
BUCKET_NAME = os.getenv("BUCKET_NAME")
KEY = 'soccarena.json'

#https://widget.eversports.com/api/slot?facilityId=24652&sport=fussball&startDate=2019-02-13&courts[]=46524&courts[]=46525&courts[]=46526&courts[]=46527&courts[]=46528&courts[]=46529

def lambda_handler(event, context):

    s3_resource = boto3.resource('s3')
    #read previous calender from s3
    stored_socckalender = s3_resource.Object(BUCKET_NAME,KEY)
    file_content = stored_socckalender.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    #print(json_content)

    #read soccarena calendar from web
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request('GET', 'https://buchen.soccarena-olympiapark.de/frontend/calendar/rendering')
    socckalender=json.loads(r.data.decode('utf-8'))

    #compare calendar with previous instance
    if socckalender==json_content:
        #print('the same')
        return {
            'statusCode': 201,
            'body': 'Soccer Crawler - no changes'
        }
    else:
        if json_content["days"].keys()!=socckalender["days"].keys():
            message_text="good morning, repeating slots for Soccarena(Olympiapark): "+chr(10)
        else:
            message_text="hi guys, here are some changes in Soccarena(Olympiapark): "+chr(10)
     #   print("different(uploaded to s3)")

    #set a message for channel based on calender data
    message_text_day=""
    for days in socckalender["days"]:
        slots_count=0
        message_text_day=days+chr(10)
        message_text_court=""
        for courts in socckalender["days"][days]["slots"]:
            slots_count=0
            message_text_slot=""
            for slots in socckalender["days"][days]["slots"][courts]["slots"]:
                if slots > '16:30':
                    try:
                        if socckalender["days"][days]["slots"][courts]["slots"][slots]["label"]=="free":
                            slots_count=slots_count+1
                            if slots_count>1: #socckalender["days"][days]["slots"][courts]["slots"][next_slot]["label"]=="free":
                                if slots_count>3: slots_count=3
                                slot_time = datetime.strptime(days+' '+slots, '%d.%m.%Y %H:%M')
                                #maybe using slots size
                                first_slot = datetime.strftime(slot_time - timedelta(minutes=30*slots_count), '%H:%M')
                                #print(days+' '+socckalender["days"][days]["slots"][courts]["field"]["name"]+' '+first_slot+'-'+slots)
                                message_text_slot=message_text_slot+'        '+first_slot+'-'+slots+chr(10)
                    except KeyError:#not all have "label"
                        slots_count=0
                        continue
            if message_text_slot!="":
                message_text_day=message_text_day+"    "+socckalender["days"][days]["slots"][courts]["field"]["name"]+chr(10)+message_text_slot
        message_text=message_text+message_text_day

    #print(message_text)

    # store new calender
    stored_socckalender.put(Body=json.dumps(socckalender))

    #send message in chat
    bot.sendMessage(chat_id=my_chat, text=message_text)

    return {
        'statusCode': 200,
        'body': 'Soccer Crawler asta la vista'
    }


r = lambda_handler("", "")
print(r)