from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
import json
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import (
    CommentEvent, ConnectEvent, JoinEvent, GiftEvent,
    LikeEvent, FollowEvent, EnvelopeEvent, LiveEndEvent, ShareEvent
)
from datetime import datetime 

# Variables 
likc=0
gift=0
dollar=0
userc=0
clientid=""
start_time = ""
time_t=""
uname=""
hlikc,hgift,hdollar,huserc,htime_t=0,0,0,0,0
dlikc,dgift,ddollar,duserc,dtime_t=0,0,0,0,0
wlikc,wgift,wdollar,wuserc,wtime_t=0,0,0,0,0
mlikc,mgift,mdollar,muserc,mtime_t=0,0,0,0,0
stats_key={"hlikc":0,"hgift":0,"hdollar":0,"huserc":0,"htime_t":0,
"dlikc":0,"dgift":0,"ddollar":0,"duserc":0,"dtime_t":0,
"wlikc":0,"wgift":0,"wdollar":0,"wuserc":0,"wtime_t":0,
"mlikc":0,"mgift":0,"mdollar":0,"muserc":0,"mtime_t":0}

#program start

edge=webdriver.Edge()
edge.maximize_window()
edge.get("file:///"+os.getcwd()+"/index.html")
edge.implicitly_wait(2)
text=edge.find_element(By.ID,"username")
butoon=edge.find_element("id","button-addon2")
while butoon.is_enabled():
    time.sleep(1)
clientid=text.get_property("value")
text.clear()
edge.execute_script("document.getElementById('button-addon2').disabled=false")
client=TikTokLiveClient(unique_id=clientid)
# functions start

def clientstart():
    global stats_key,likc,userc,gift,dollar,time_t,clientid,uname,client,text,edge
    try:
        clientid=text.get_property("value")
        text.clear()
        edge.execute_script("document.getElementById('button-addon2').disabled=false")
        print(clientid)
        client = TikTokLiveClient(unique_id=clientid)
        client.start()
        client.run()
    except Exception as e:
        print("User offline",e)
        edge.execute_script(f"document.getElementById('status').class='offline-status'")
        stats_key.update({"Like Count":likc,"View Count":userc,"Gift Count":gift,"Dollar Count":dollar,"Total time":time_t})
        with open(os.getcwd()+"\\userdata.json","a+") as f:
            clientdata={clientid:{"clientid":clientid,"User Name":uname,"stats":stats_key}}
            json.dump(clientdata,f)
def update():
    global likc,gift,dollar,userc,time_t,stats_key
    userc=client.viewer_count
    time_t = datetime.now() - start_time
    time_t=str(time_t)[:7]
    edge.execute_script(f"document.getElementById('currentv').textContent={userc};document.getElementById('currentt').textContent='{time_t}';\
            document.getElementById('currentl').textContent={likc};document.getElementById('currentg').textContent={gift};\
            document.getElementById('currentd').textContent={dollar}")
    for i in stats_key.keys():
        edge.exceute_script(f"document.getElementById('{i}').textContent='{stats[i]}';")
    if not butoon.is_enabled() and text.get_property("value")!="":
        print("Another")
        clientstart()
    
    
@client.on("connect")
async def on_connect(event: ConnectEvent):
    print("Connected to Room ID:", client.room_id)
    global clientid,edge,uname,start_time
    image_link=client.room_info["owner"]["avatar_medium"]["url_list"][0]
    uname=client.room_info["owner"]["nickname"].title()
    edge.execute_script(f"document.getElementsByClassName('card-img-top')[0].src='{image_link}';document.getElementById('fname').textContent='{uname}';document.getElementById('status').className='live-status'")
    start_time=datetime.now()
    update()
    with open("username.json","a+") as f:
        try:
            if f[clientid]:
                stats=f[clientid]["stats"]
                for i in stats_key.keys():
                    stats_key[i]=stats[i]
        except:
            print("User not in Database")

@client.on("join")
async def on_join(event: JoinEvent):
    #print(f"{event.user.nickname} -> joined the event")
    update()


@client.on("like")
async def on_like(event: LikeEvent):
    global likc,edge
    likc+=1
    print(f"@{event.user.unique_id} liked the stream!")
    edge.execute_script(f"document.getElementById('currentl').textContent={likc}")
    update()


@client.on("gift")
async def on_gift(event: GiftEvent):
    global gift,edge
    gift+=1    
    if event.gift.streakable and not event.gift.streaking:
        print(f"{event.user.unique_id} sent {event.gift.count}x \"{event.gift.info.name}\"")
    elif not event.gift.streakable:
        print(f"{event.user.unique_id} sent \"{event.gift.info.name}\"")
    edge.execute_script(f"document.getElementById('currentg').textContent={gift}")


@client.on("error")
async def on_error(error: Exception):
    #print(error)
    if isinstance(error, SomeRandomError):
        print("Handle some error!")
        return

    
@client.on("envelope")
async def on_envelope(event: EnvelopeEvent):
    global dollar
    dollar+=1
    print(f"{event.treasure_box_user.unique_id} -> {event.treasure_box_data}")
    edge.execute_script(f"document.getElementById('currentd').textContent={dollar}")


@client.on("live_end")
async def on_live_end(event: LiveEndEvent):
    print(f"Livestream ended :(")
    global stats_key,likc,userc,time_t,gift,dollar
    stats_key.update({"Like Count":likc,"View Count":userc,"Gift Count":gift,"Dollar Count":dollar,"Total time":time_t})
    with open(os.getcwd()+"\\userdata.json","a+") as f:
        clientdata={clientid:{"clientid":clientid,"User Name":uname,"stats":stats_key}}
        json.dump(clientdata,f)
client.run()
