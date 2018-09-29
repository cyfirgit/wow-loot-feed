import os
import logging
import json
import requests
import datetime

TEST_CHARACTER = {'realm': 'proudmoore', 'name': 'Volstatsz'}

def json_pull(dct):
    #Pull data from a static .json file and load it into memory.
    path = os.path.join('C:\\code\\wow-loot-feed\\', dct)
    return json.load(open(path))
    
def get_wow_feed(character):
    api_key = json_pull('api-keys.json')['blizzard']
    url = ('https://us.api.battle.net/wow/character/' + character['realm'] +
           '/' + character['name'] + '?fields=feed&locale=en_US&apikey=' +
           api_key)
    response = requests.get(url)
    return response.json()
    
def process_feed(feed):
    # Go through each event in the feed.  Look for kills and loot.  If you get
    # a loot, check the boss kills on either side (if they exist,) for which one
    # the loot should be attributed to.  Currently only cares about raid loot.

    #last_update = datetime.datetime.fromtimestamp(feed['lastModified'])
    loots = []
    last_kill = {'timestamp': False}
    last_loot = {'timestamp': False}
    for event in feed['feed']:
        if event['type'] == 'BOSSKILL':
            if last_loot['timestamp'] and last_kill['timestamp']:
                if (last_kill['timestamp'] - last_loot['timestamp'] >
                    last_loot['timestamp'] - event['timestamp']):
                    last_loot['kill'] = event
                else:
                    last_loot['kill'] = last_kill
            elif last_loot['timestamp']:
                last_loot['kill'] = event
            last_kill = event
        elif event['type'] == 'LOOT' and event['context'][0:4] == 'raid':
            last_loot = event
        if 'kill' in last_loot:
            loots.append(last_loot)
            last_loot = {'timestamp': False}
    return loots