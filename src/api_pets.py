import json
import requests
from colorama import *
from time import sleep
from datetime import datetime

from src.Battle import print_with_timestamp, merah, biru, kuning, hijau, hitam, putih, reset

init(autoreset=True)

def split_chunk(var):
    if isinstance(var, int):
        var = str(var)
    n = 3
    var = var[::-1]
    return ','.join([var[i:i + n] for i in range(0, len(var), n)])[::-1]

class UserPixel:
    def __init__(self, config):
        self.config = config
        
        self.headers = {
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": "api-clicker.pixelverse.xyz",
            "If-None-Match": 'W/"29b-JPcgLG/Nvfd8KEVQN/lMKfPaHpQ"',
            "initData": self.config['initData'],
            "Origin": "https://sexyzbot.pxlvrs.io",
            "Priority": "u=3, i",
            "Referer": "https://sexyzbot.pxlvrs.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "secret": self.config['secret'],
            "tg-id": self.config['tgId'],
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
        }

    def getUsers(self):
        url = "https://api-clicker.pixelverse.xyz/api/users"
        req = requests.get(url, headers=self.headers)
        return req.json()

    def getStats(self):
        url = "https://api-clicker.pixelverse.xyz/api/battles/my/stats"
        req = requests.get(url, headers=self.headers)
        return req.json()
    
    def getPets(self):
        data = self.getUsers()
        url = "https://api-clicker.pixelverse.xyz/api/pets"
        req = requests.get(url, headers=self.headers)
        data = req.json()
        return data['data']

    def upgrade(self, petId: str):
        url = f"https://api-clicker.pixelverse.xyz/api/pets/user-pets/{petId}/level-up"
        req = requests.post(url, headers=self.headers)
        return req.json()

    def upgradePets(self, upgrade_pets: bool):
        data = self.getUsers()
        currBalance = data['clicksCount']
        pets = self.getPets()
        url = "https://api-clicker.pixelverse.xyz/api/pets"
        req = requests.get(url, headers=self.headers)
        pets = req.json()['data']

        for pet in pets:
            if 'isMaxLevel' in pet['userPet'] and pet['userPet']['isMaxLevel']:
                print_with_timestamp(f"{hijau}{pet['name']} Is Max Level")
            elif pet['userPet']['level'] >= 39:
                print_with_timestamp(f"{kuning}{pet['name']} has reached lvl {putih}{pet['userPet']['level']}")
                continue
            else:
                if upgrade_pets:
                    if currBalance >= pet['userPet']['levelUpPrice']:
                        self.upgrade(pet['userPet']['id'])
                        print_with_timestamp(f"{hijau}Success upgrade {kuning}{pet['name']}")
                        currBalance -= pet['userPet']['levelUpPrice']
                    else:
                        print_with_timestamp(f"{hijau}{pet['name']} cost: {putih}-{split_chunk(str(int(pet['userPet']['levelUpPrice'] - currBalance)))} {kuning}left!")
                else:
                    if currBalance >= pet['userPet']['levelUpPrice']:
                        print_with_timestamp(f"{kuning}{pet['name']} available for upgrade")
                    else:
                        print_with_timestamp(f"{hijau}{pet['name']} cost: {putih}-{split_chunk(str(int(pet['userPet']['levelUpPrice'] - currBalance)))} {kuning}left!")
            
        print_with_timestamp(f"{hijau}Balance after : {putih}{split_chunk(str(int(currBalance)))}")
        print_with_timestamp(f"{hitam}{'~' * 42}\r")


    def isBroken(self):
        url = "https://api-clicker.pixelverse.xyz/api/tasks/my"
        req = requests.get(url, headers=self.headers)
        return req.status_code == 500
