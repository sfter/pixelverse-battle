import asyncio
import json
import sys
import time
import os
import hmac
import hashlib
from datetime import datetime
import websockets
from colorama import *
from random import uniform, randint
import requests

init(autoreset=True)
merah = Fore.LIGHTRED_EX
putih = Fore.LIGHTWHITE_EX
hijau = Fore.LIGHTGREEN_EX
kuning = Fore.LIGHTYELLOW_EX
biru = Fore.LIGHTBLUE_EX
reset = Style.RESET_ALL
hitam = Fore.LIGHTBLACK_EX

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def countdown_timer(seconds):
    while seconds:
        menit, detik = divmod(seconds, 60)
        jam, menit = divmod(menit, 60)
        jam = str(jam).zfill(2)
        menit = str(menit).zfill(2)
        detik = str(detik).zfill(2)
        print(f"{putih}preparing your data {hijau}{jam}:{menit}:{detik} ", flush=True, end="\r")
        seconds -= 1
        time.sleep(1)
    print("                                ", flush=True, end="\r")
        
def print_with_timestamp(message, end="\n", flush=True):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sys.stdout.write(f"{hitam}[{current_time}] {message}{end}")
    if flush:
        sys.stdout.flush()

def split_chunk(var):
    if isinstance(var, int):
        var = str(var)
    n = 3
    var = var[::-1]
    return ','.join([var[i:i + n] for i in range(0, len(var), n)])[::-1]

class Battle:

    def __init__(self, initData):
        self.url = 'https://api-clicker.pixelverse.xyz/api/users'
        self.tgId = ''
        self.secret = self.get_secret(self.tgId)
        self.initData = initData
        self.websocket: websockets.WebSocketClientProtocol = None
        self.battleId = ""
        self.superHit = False
        self.strike = {
            "defense": False,
            "attack": False
        }
        self.stop_event = asyncio.Event()
        self.stats = None
        self.min_hit_speed = 0.09
        self.max_hit_speed = 0.12
    
    def get_secret(self, userid):
        rawr = "adwawdasfajfklasjglrejnoierjboivrevioreboidwa"
        secret = hmac.new(
            rawr.encode("utf-8"), str(userid).encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return secret
    
    async def sendHit(self):
        while not self.stop_event.is_set():
            if self.superHit:
                await asyncio.sleep(uniform(self.min_hit_speed, self.max_hit_speed))
                continue
            content = [
                "HIT",
                {
                    "battleId": self.battleId
                }
            ]
            try:
                await self.websocket.send(f"42{json.dumps(content)}")
            except Exception as e:
                return
            await asyncio.sleep(uniform(self.min_hit_speed, self.max_hit_speed))

    async def listenerMsg(self):
        while not self.stop_event.is_set():
            try:
                data = await self.websocket.recv()
            except Exception as err:
                print_with_timestamp(f"{merah}{err}")
                self.stop_event.set()
                return
    
            if data.startswith('42'):
                data = json.loads(data[2:])
                if data[0] == "HIT":
                    player1_energy = data[1]['player1']['energy']
                    player2_energy = data[1]['player2']['energy']
                    player1_name = self.player1['name']
                    player2_name = self.player2['name']
                    # Cek jika username pemain adalah tgId
                    if player1_name == self.tgId:
                        player1_name = "you"
                    if player2_name == self.tgId:
                        player2_name = "you"
                    if player1_energy < player2_energy:
                        player1_energy_color = merah
                        player2_energy_color = hijau
                    else:
                        player1_energy_color = hijau
                        player2_energy_color = merah

                    print_with_timestamp(
                        f"{kuning}{player1_name} "
                        f"{player1_energy_color}[{player1_energy}]"
                        f"{player2_energy_color}[{player2_energy}] "
                        f"{kuning}{player2_name}  ",
                        end="\r"
                    )
                elif data[0] == "SET_SUPER_HIT_PREPARE":
                    self.superHit = True
                    print_with_timestamp(f"{kuning}Super hit preparation started         ", end="\r", flush=True)

                elif data[0] == "SET_SUPER_HIT_ATTACK_ZONE":
                    content = [
                        "SET_SUPER_HIT_ATTACK_ZONE",
                        {
                            "battleId": self.battleId,
                            "zone": randint(1, 4)
                        }
                    ]
                    try:
                        await self.websocket.send(f"42{json.dumps(content)}")
                        self.strike['attack'] = True
                        print_with_timestamp(f"{kuning}Super hit attack zone set      ", end="\r", flush=True)
                    except Exception as e:
                        print_with_timestamp(f"{merah}Error sending super hit attack zone: {e}", flush=True)

                elif data[0] == "SET_SUPER_HIT_DEFEND_ZONE":
                    content = [
                        "SET_SUPER_HIT_DEFEND_ZONE",
                        {
                            "battleId": self.battleId,
                            "zone": randint(1, 4)
                        }
                    ]
                    try:
                        await self.websocket.send(f"42{json.dumps(content)}")
                        self.strike['defense'] = True
                        print_with_timestamp(f"{kuning}Super hit defend zone set      ", end="\r", flush=True)
                    except Exception as e:
                        print_with_timestamp(f"{merah}Error sending super hit defend zone: {e}", flush=True)

                elif data[0] == "END":
                    await asyncio.sleep(0.4)
                    print('')
                    if data[1]['result'] == "WIN":
                        print_with_timestamp(f"{hijau}Congratulations, you are victory!")
                        print_with_timestamp(f"{hijau}Victory reward: {putih}+{split_chunk(str(int(data[1]['reward'])))}")
                    else:
                        print_with_timestamp(f"{merah}Defeat, better luck next time.")
                        print_with_timestamp(f"{merah}Defeat penalty: {putih}-{split_chunk(str(int(data[1]['reward'])))}")

                    await self.websocket.recv()
                    self.stop_event.set()
                    return

                try:
                    if (self.strike['attack'] and not self.strike['defense']) or (self.strike['defense'] and not self.strike['attack']):
                        await self.websocket.recv()
                        await self.websocket.recv()
                    if self.strike['attack'] and self.strike['defense']:
                        await self.websocket.recv()
                        await self.websocket.send("3")
                        await self.websocket.recv()

                        # Reset superHit and strike after super hit attack and defense are done
                        self.superHit = False
                        self.strike['attack'] = False
                        self.strike['defense'] = False
                        print_with_timestamp(f"{kuning}Super hit completed, who win ?       ", end="\r", flush=True)
                except Exception as e:
                    print_with_timestamp(f"{merah}Error in strike handling: {e}")
                    pass

    async def handleWssFreeze(self, seconds: int):
        timeToReach = time() + seconds

        while not self.stop_event.is_set():
            if time() > timeToReach:
                self.websocket.close()
            await asyncio.sleep(0.001)

    async def connect(self):
        uri = "wss://api-clicker.pixelverse.xyz/socket.io/?EIO=4&transport=websocket"
        retry_count = 0
        while retry_count < 10:
            try:
                async with websockets.connect(uri) as websocket:
                    self.websocket = websocket
                    data = await websocket.recv()
                    content = {
                        "tg-id": self.tgId,
                        "secret": self.secret,
                        "initData": self.initData
                    }

                    await websocket.send(f"40{json.dumps(content)}")
                    await websocket.recv()
                    
                    data = await websocket.recv()
                    if not data:
                        continue
                    data = json.loads(data[2:])
                    self.battleId = data[1]['battleId']
                    self.player1 = {
                        "name": data[1]['player1']['username']
                    }
                    self.player2 = {
                        "name": data[1]['player2']['username']
                    }
                    
                    print_with_timestamp(f"{kuning}Found a new challenger:")
                    print_with_timestamp(f"{hijau}{data[1]['player1']['username']}{putih} VS {hijau}{data[1]['player2']['username']}")
                    
                    for i in range(5, -1, -1):
                        print_with_timestamp(f"{kuning}countdown {hitam}[{i}] {kuning}to the battle!", end="\r")
                        await asyncio.sleep(1)
                    print_with_timestamp(f"{hijau}The battle has begun... fight!", end="\r")

                    print('')

                    self.stats = {
                        'winsReward': 0,
                        'losesReward': 0
                    }

                    listenerMsgTask = asyncio.create_task(self.listenerMsg())
                    hitTask = asyncio.create_task(self.sendHit())

                    await asyncio.gather(listenerMsgTask, hitTask)
                break
            except websockets.exceptions.ConnectionClosed as e:
                print_with_timestamp(f"{merah}WebSocket connection closed: ", flush=True)
                print_with_timestamp(f"{merah}{e}", flush=True)
                retry_count += 1
                print_with_timestamp(f"{kuning}Retrying connection ({retry_count}/10)...",end="\n", flush=True)
                await asyncio.sleep(5)
            except requests.exceptions.RequestException as e:
                print_with_timestamp(f"{merah}HTTP connection error: ", flush=True)
                print_with_timestamp(f"{merah}{e}", flush=True)
                retry_count += 1
                print_with_timestamp(f"{kuning}Retrying connection ({retry_count}/10)...",end="\n", flush=True)
                await asyncio.sleep(5)
            except json.JSONDecodeError as e:
                print_with_timestamp(f"{merah}Error decoding JSON: ", flush=True)
                print_with_timestamp(f"{merah}{e}", flush=True)
                retry_count += 1
                print_with_timestamp(f"{kuning}Retrying connection ({retry_count}/10)...",end="\n", flush=True)
                await asyncio.sleep(5)
            except Exception as e:
                print_with_timestamp(f"{merah}Error connecting to websocket: ", flush=True)
                print_with_timestamp(f"{merah}{e}", flush=True)
                retry_count += 1
                print_with_timestamp(f"{kuning}Retrying connection ({retry_count}/10)...",end="\n", flush=True)
                await asyncio.sleep(5)
        else:
            print_with_timestamp(f"{merah}Max retries reached. Exiting...")
            
if __name__ == "__main__":
    try:
        asyncio.run(Battle())
    except KeyboardInterrupt:
        print_with_timestamp(f"{merah}Program terminated by user.")
        sys.exit()
