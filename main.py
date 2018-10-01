import os
import logging
import json
import requests
import datetime
import io

TEST_CHARACTER = {'realm': 'proudmoore', 'name': 'Volstatsz'}

ENCOUNTERS = [
    {
        "id": 2144,
        "name": "Taloc",
        "npcID": 137119
    },
    {
        "id": 2141,
        "name": "MOTHER",
        "npcID": 135452
    },
    {
        "id": 2128,
        "name": "Fetid Devourer",
        "npcID": 133298
    },
    {
        "id": 2136,
        "name": "Zek'voz, Herald of N'zoth",
        "npcID": 134445
    },
    {
        "id": 2134,
        "name": "Vectis",
        "npcID": 134442
    },
    {
        "id": 2145,
        "name": "Zul, Reborn",
        "npcID": 138967
    },
    {
        "id": 2135,
        "name": "Mythrax the Unraveler",
        "npcID": 134546
    },
    {
        "id": 2122,
        "name": "G'huun",
        "npcID": 132998
    }
]

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

def characters_crawler():
    #Search WCL ranks for new characters.
    try:
        with io.open('characters.json', encoding='utf-8') as f:
            characters = json.load(f)
    except:
        characters = {}
    for encounter in ENCOUNTERS:
        #search each page of the encounter, merging into the overall data
        page = 1
        has_more_pages = True
        while has_more_pages == True and page <= 200:
            print('Requesting page {} of ranks for {}'.format(page, encounter['name']))
            api_key = json_pull('api-keys.json')['warcaftlogs']
            url = ('https://www.warcraftlogs.com:443/v1/rankings/encounter/' +
                    str(encounter['id']) + '?api_key=' + api_key + '&page=' + 
                    str(page) + '&difficulty=4')
            response = requests.get(url).json()
            for character in response['rankings']:
                character_unique = (character['name'] + '_' + 
                                    character['serverName'] + '_' + 
                                    character['regionName'])
                if not character_unique in characters:
                    print('New character {} found'.format(character_unique))
                    characters[character_unique] = {
                        'name': character['name'],
                        'server': character['serverName'],
                        'regaion': character['regionName'],
                        'class': character['class']
                    }
            page += 1
            has_more_pages = response['hasMorePages']
    with io.open('characters.json', 'w', encoding='utf-8') as f:
        json.dump(characters, f, ensure_ascii=False)



def encounters_crawler(last_crawl):
    #Search characters in DB for new encounters.
    pass