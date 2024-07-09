import asyncio
import json
import sys
import os
import argparse
from datetime import datetime
from colorama import *
from src.Battle import Battle
from src.Battle import countdown_timer, split_chunk, clear_screen
from src.Battle import print_with_timestamp, merah, biru, kuning, hijau, hitam, putih
from src.api_pets import UserPixel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

init(autoreset=True)

def print_banner():
    banner = r"""
    ██╗████████╗███████╗     ██╗ █████╗ ██╗    ██╗
    ██║╚══██╔══╝██╔════╝     ██║██╔══██╗██║    ██║
    ██║   ██║   ███████╗     ██║███████║██║ █╗ ██║
    ██║   ██║   ╚════██║██   ██║██╔══██║██║███╗██║
    ██║   ██║   ███████║╚█████╔╝██║  ██║╚███╔███╔╝
    ╚═╝   ╚═╝   ╚══════╝ ╚════╝ ╚═╝  ╚═╝ ╚══╝╚══╝  """
    print(Fore.GREEN + Style.BRIGHT + banner + Style.RESET_ALL)
    print(hijau + "    Pixeltap by Pixelverse Auto Battle")
    print(merah + f"    NOT FOR SALE = Free to use")
    print(merah + f"    Please {hijau}'git pull{merah}' to update this bot")

def parse_query_string(query):
    params = {}
    for part in query.split("&"):
        key, value = part.split("=")
        params[key] = value
    return params

async def update_user_info(user):
    users = user.getUsers()
    stats = user.getStats()

    wins = stats.get('wins', 0)
    loses = stats.get('loses', 0)
    battles_count = stats.get('battlesCount', 0)
    wins_reward = stats.get('winsReward', 0)
    loses_reward = stats.get('losesReward', 0)
    win_rate = (wins / battles_count) * 100 if battles_count > 0 else 0

    print(f"{hijau}{'~' * 62}\r")
    print_with_timestamp(f"{hijau}User: {putih}{users.get('username', 'Unknown')} {kuning}| Balance: {putih}{split_chunk(str(int(users.get('clicksCount', 0))))}")
    print_with_timestamp(f"{hijau}W{kuning}/{merah}L {hijau}: "
                         f"{hijau}{split_chunk(str(wins))}{kuning}/{merah}{split_chunk(str(loses))}\t "
                         f"{kuning}| {hijau}Wins: {putih}{split_chunk(str(wins_reward))}")
    print_with_timestamp(f"{hijau}Match: {putih}{split_chunk(str(battles_count))}\t "
                         f"{kuning}| {merah}Loses: {putih}{split_chunk(str(loses_reward))}")
    print_with_timestamp(f"{hijau}Winrate: {putih}{win_rate:.2f}%\t "
                         f"{kuning}| {biru}Earned: {putih}{split_chunk(str(wins_reward + loses_reward))}")

async def main():
    arg = argparse.ArgumentParser()
    arg.add_argument('--upgrade', help="Set upgrade_pets to True", action='store_true')
    args = arg.parse_args()
    clear_screen()
    print_banner()
    try:
        init()

        with open("initdata.txt", "r") as file:
            datas = file.read().splitlines()
        while True:
            for no, data in enumerate(datas):
                battle = Battle(data)
                await battle.connect()
                del battle

            # user.upgradePets(upgrade_pets=config['upgrade_pets'])
            countdown_timer(15)
            await asyncio.sleep(1)
  
    except Exception as e:
        print(e)
