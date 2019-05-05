import telegram
import certifi
import urllib3
import json
import boto3
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

print("start")
#s3 setup
BUCKET_NAME = 'soccer.crawler'
KEY = 'soccerworld.json'
s3_resource = boto3.resource('s3')
stored_socckalender_obj = s3_resource.Object(BUCKET_NAME,KEY)
try:
    stored_socckalender_json = json.loads(stored_socckalender_obj.get()['Body'].read().decode('utf-8'))
    #print(json_content)
except s3_resource.meta.client.exceptions.NoSuchKey:
    stored_socckalender_json = json.loads('{"days": {"key":1}}')
    print("no moosach file on s3")


soccer_date=datetime.now()
soccer_date_str=soccer_date.strftime("%Y-%m-%d")

#read soccarena calendar from web
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
r = http.request('GET', 'https://widget.eversports.com/api/slot?facilityId=24652&sport=fussball&startDate='+soccer_date_str+'&courts[]=46524&courts[]=46525&courts[]=46526&courts[]=46527&courts[]=46528&courts[]=46529')
socckalender=json.loads(r.data.decode('utf-8'))

#compare calendar with previous instance
if socckalender==stored_socckalender_json :
    print('the same')
#    quit(101)
#else:
#    if stored_socckalender_json ["days"].keys()!=socckalender["days"].keys():
#        message_text="good morning, repeating slots for Soccarena(Olympiapark): "+chr(10)
#    else:
stored_socckalender_obj.put(Body=json.dumps(socckalender))
#print("different(uploaded to s3)")
message_text="... and here are some slots in Soccerworld(Moosach): "+chr(10)

courts = [46524,46525,46526,46527,46528,46529]
timeslots=["17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30"]

#set a message for channel based on calender data
message_text_day=""
slots_count=0

for single_date in (soccer_date + timedelta(n) for n in range(7)):
    message_text_day=message_text_day+single_date.strftime("%d.%m.%Y")+chr(10)
    for court in courts:
        for timeslot in timeslots:
            slots_count=slots_count+1
            if slots_count>1: #socckalender["days"][days]["slots"][courts]["slots"][next_slot]["label"]=="free":
                if slots_count>3: slots_count=3
                slot_time = datetime.strptime(single_date.strftime("%d.%m.%Y")+' '+timeslot, '%d.%m.%Y %H:%M')
                #maybe using slots size
                first_slot = datetime.strftime(slot_time - timedelta(minutes=30*slots_count), '%H:%M')
                #print(days+' '+socckalender["days"][days]["slots"][courts]["field"]["name"]+' '+first_slot+'-'+slots)
                message_text_slot=message_text_slot+'   '+first_slot+'-'+timeslot+chr(10)
            for slot in socckalender["slots"]:
                if slot["date"]==single_date.strftime("%Y-%m-%d") and slot["court"]==court and slot["start"] == timeslot.replace(':',''):
                    slots_count=0
                    message_text_slot=""
                    break
            message_text_day = message_text_day + message_text_slot

print(message_text  + message_text_day)
#bot.sendMessage(chat_id="-", text=message_text)
