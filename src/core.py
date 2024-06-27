import asyncio
import json
import sys
import os
import argparse
import random
from src.Battle import Battle
from src.Battle import countdown_timer, split_chunk,clear_screen
from src.Battle import print_with_timestamp, merah,biru,kuning,hijau,hitam,putih,reset
from src.api_pets import UserPixel
from colorama import *
from datetime import datetime

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

async def update_user_info(user):
    users = user.getUsers()
    stats = user.getStats()
    winRate = (stats['wins'] / stats['battlesCount']) * 100 if stats['battlesCount'] > 0 else 0

    print(f"{hijau}{'~' * 62}\r")
    print_with_timestamp(f"{kuning}User: {users['username']} | Balance: {split_chunk(str(int(users['clicksCount'])))}")
    print_with_timestamp(f"{hijau}W{kuning}/{merah}L {hijau}: "
    f"{hijau}{split_chunk(str(stats['wins']))}{kuning}/{merah}{split_chunk(str(stats['loses']))}\t "
    f"{kuning}| {hijau}Wins: {split_chunk(str(stats['winsReward']))}")
    print_with_timestamp(f"{biru}Match: {split_chunk(str(stats['battlesCount']))}\t "
    f"{kuning}| {merah}Loses: {split_chunk(str(stats['losesReward']))}")
    print_with_timestamp(f"{hijau}Winrate: {putih}{winRate:.2f}%\t " 
    f"{kuning}| {biru}Earned: {split_chunk(str(stats['winsReward'] + stats['losesReward']))}")
async def main():
    arg = argparse.ArgumentParser()
    arg.add_argument('--config', help="Custom config file (default: config.json)", default="config.json")

    args = arg.parse_args()

    clear_screen()
    print_banner()
    try:
        init()
        with open(f"./{args.config}", 'r') as config_file:
            config = json.load(config_file)
        user = UserPixel(config)
        await update_user_info(user)

        while True:
            battle = Battle()
            await battle.connect()
            del battle

            user.upgradePets(upgrade_pets=config['upgrade_pets'])
            # Countdown Timer sebelum memulai pertempuran baru
            countdown_timer(10)
            sleepTime = random.randint(config['min_sleep_time'], config['max_sleep_time'])
            print(f"sleep {sleepTime} seconds")
            await asyncio.sleep(sleepTime)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()

