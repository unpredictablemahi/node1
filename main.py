import os
import json
import uuid
import time
import asyncio
import aiofiles
import argparse
import httpx as hatetepe
from datetime import datetime
from colorama import Fore, Style, init
from urllib.parse import parse_qs
from fake_useragent import UserAgent
from base64 import urlsafe_b64decode
from pyfiglet import Figlet

init(autoreset=True)
gray = Fore.LIGHTBLACK_EX
green = Fore.LIGHTGREEN_EX
blue = Fore.LIGHTBLUE_EX
red = Fore.LIGHTRED_EX
reset = Style.RESET_ALL

# Define the print_intro function for the banner
def print_intro():
    f = Figlet(font='starwars')
    ascii_art = f.renderText('WAT B0T')
    print('\033[94m' + ascii_art + '\033[0m')  # Blue color for the title
    print('\033[92m' + '📡 WAT POWERED BY Gamee' + '\033[0m')  # Green color for the description
    print('\033[96m' + '👨‍💻 Created by: CIPHER' + '\033[0m')  # Cyan color for the creator
    print('\033[95m' + '🔍 Initializing WAT B0T...' + '\033[0m')  # Magenta color for the initializing message
    print("════════════════════════════════════════════════════════════")
    print("║       Follow us for updates and support:                 ║")
    print("║                                                          ║")
    print("║     Twitter:                                             ║")
    print("║     https://twitter.com/cipher_airdrop                   ║")
    print("║                                                          ║")
    print("║     Telegram:                                            ║")
    print("║     - https://t.me/+tFmYJSANTD81MzE1                     ║")
    print("╚════════════════════════════════════════════════════════════")

    # Prompt for user confirmation
    answer = input('\033[91mWill you FC* Gamee Airdrop? (Y/N): \033[0m')  # Red color for the prompt
    if answer.lower() != 'y':
        print('\033[91mAborting execution.\033[0m')  # Red color for abort message
        exit(1)

class Config:
    def __init__(self, countdown, interval, use_ticket_to_spin, max_use_ticket_to_spin):
        self.countdown = countdown
        self.interval = interval
        self.use_ticket_to_spin = use_ticket_to_spin
        self.max_use_ticket_to_spin = max_use_ticket_to_spin

class GameeBot:
    def __init__(self, query: str, config: Config):
        parse_data = lambda data: {key: value[0] for key, value in parse_qs(data).items()}
        parser = parse_data(query)
        user = parser.get("user")
        if user is None:
            self.log(f"{red}[ERROR] No user data in your query, ensure your query is correct!")
            return
        user_data = json.loads(user)
        self.id = str(user_data.get("id"))
        first_name = user_data.get("first_name")
        self.log(f"{green}[SUCCESS] Logged in as {first_name}")
        self.uuid_file = "gamee_uuid.json"
        self.ua_file = "gamee_useragent.json"
        self.token_file = "gamee_tokens.json"
        self.gamee_url = "https://api.gamee.com/"
        self.query = query
        self.config = config

    @staticmethod
    def log(msg):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{gray}[{now}]{reset} {msg}{reset}")

    def is_expired(self, token):
        if token is None:
            return True
        header, payload, sign = token.split(".")
        decoded_payload = urlsafe_b64decode(payload + "==")
        json_payload = json.loads(decoded_payload)
        exp = int(json_payload.get("exp", 0))
        now = int(time.time())
        if (now + 300) > exp:
            return True
        return False

    def convert_token_value(self, data):
        return data / 1000000

    async def http(self, url, data=None):
        while True:
            try:
                if not os.path.exists("http.log"):
                    await aiofiles.open("http.log", "a")
                log_size = os.path.getsize("http.log")
                if ((log_size / 1024) / 1024) > 1:
                    async with aiofiles.open("http.log", "w") as hw:
                        await hw.write("")
                if data is None:
                    res = await self.ses.get(url)
                elif data == "":
                    res = await self.ses.post(url)
                else:
                    res = await self.ses.post(url, data=data)
                async with aiofiles.open("http.log", "a", encoding="utf-8") as hw:
                    await hw.write(f"{res.text}\n")
                if "<title>" in res.text:
                    self.log(f"{blue}[DEBUG] Failed to get response JSON!")
                    await self.countdown(5)
                    continue
                return res
            except (hatetepe.TimeoutException, hatetepe.NetworkError):
                self.log(f"{red}[ERROR] Connection error or timeout!")

    async def check_ip(self):
        res = await self.http("https://ipinfo.io/json")
        ip = res.json().get("ip")
        city = res.json().get("city")
        country = res.json().get("country")
        self.log(f"{green}[SUCCESS] Proxy IP: {ip}")
        self.log(f"{green}[SUCCESS] City: {city} | Country: {country}")

    async def login(self, tg_data):
        data = {
            "jsonrpc": "2.0",
            "id": "user.authentication.loginUsingTelegram",
            "method": "user.authentication.loginUsingTelegram",
            "params": {"initData": tg_data},
        }
        while True:
            res = await self.http(self.gamee_url, json.dumps(data))
            result = res.json().get("result")
            if result is None:
                self.log(f"{red}[ERROR] Something went wrong, check http.log!")
                return False
            self.log(f"{green}[SUCCESS] Login successful!")
            access_token = result.get("tokens").get("authenticate")
            return access_token

    async def spin(self):
        daily_get_prizes = {
            "jsonrpc": "2.0",
            "id": "dailyReward.getPrizes",
            "method": "dailyReward.getPrizes",
            "params": {},
        }
        daily_claim_prize = {
            "jsonrpc": "2.0",
            "id": "dailyReward.claimPrize",
            "method": "dailyReward.claimPrize",
            "params": {},
        }
        buy_spin_ticket = {
            "jsonrpc": "2.0",
            "id": "dailyReward.buySpinUsingTickets",
            "method": "dailyReward.buySpinUsingTickets",
            "params": {},
        }

        res = await self.http(self.gamee_url, json.dumps(daily_get_prizes))
        result = res.json().get("result")
        if result is None:
            self.log(f"{red}[ERROR] Result is None!")
            return False
        daily_reward = result.get("dailyReward")
        daily_spin_count = daily_reward.get("spinsCountAvailable")
        ticket_price = daily_reward.get("dailyRewardBonusSpinsPriceTickets")
        tickets = res.json()["user"]["tickets"]["count"]
        self.log(f"{green}[SUCCESS] Available tickets: {tickets}")
        self.log(f"{green}[SUCCESS] Free spins available: {daily_spin_count}")
        self.log(f"{green}[SUCCESS] Price to spin: {ticket_price} tickets")
        if daily_spin_count > 0:
            for i in range(daily_spin_count):
                res = await self.http(self.gamee_url, json.dumps(daily_claim_prize))
                reward_type = res.json()["result"]["reward"]["type"]
                key = "usdCents" if reward_type == "money" else reward_type
                reward = res.json()["result"]["reward"][key]
                self.log(f"{green}[SUCCESS] Spin reward: {reward} {reward_type}")
        if self.config.use_ticket_to_spin is False:
            return
        self.log(f"{blue}[DEBUG] Starting ticket-based spin!")
        while True:
            if tickets < ticket_price:
                self.log(f"{blue}[DEBUG] Not enough tickets to spin!")
                return
            if ticket_price > self.config.max_use_ticket_to_spin:
                self.log(f"{blue}[DEBUG] Max ticket usage reached!")
                return
            res = await self.http(self.gamee_url, json.dumps(buy_spin_ticket))
            res = await self.http(self.gamee_url, json.dumps(daily_claim_prize))
            reward_type = res.json()["result"]["reward"]["type"]
            key = "usdCents" if reward_type == "money" else reward_type
            reward = res.json()["result"]["reward"][key]
            self.log(f"{green}[SUCCESS] Ticket-based spin reward: {reward} {reward_type}")
            res = await self.http(self.gamee_url, json.dumps(daily_get_prizes))
            result = res.json().get("result")
            daily_reward = result.get("dailyReward")
            daily_spin_count = daily_reward.get("spinsCountAvailable")
            ticket_price = daily_reward.get("dailyRewardBonusSpinsPriceTickets")
            tickets = res.json()["user"]["tickets"]["count"]
            self.log(f"{green}[SUCCESS] Available tickets: {tickets}")
            self.log(f"{green}[SUCCESS] Price to spin: {ticket_price} tickets")

    async def mining(self):
        mining_event_id = 26
        mining_event_data = {
            "jsonrpc": "2.0",
            "id": "miningEvent.get",
            "method": "miningEvent.get",
            "params": {"miningEventId": mining_event_id},
        }
        start_mining_data = {
            "jsonrpc": "2.0",
            "id": "miningEvent.startSession",
            "method": "miningEvent.startSession",
            "params": {"miningEventId": mining_event_id},
        }
        claim_mining_data = {
            "jsonrpc": "2.0",
            "id": "miningEvent.claim",
            "method": "miningEvent.claim",
            "params": {"miningEventId": mining_event_id},
        }
        res = await self.http(self.gamee_url, json.dumps(mining_event_data))
        assets = res.json()["user"]["assets"]
        for asset in assets:
            currency = asset["currency"]["ticker"]
            amount = asset["amountMicroToken"] / 1000000
            self.log(f"{green}Balance: {amount} {currency}")
        mining_event = res.json()["result"]["miningEvent"]["miningUser"]
        if mining_event is None:
            self.log(f"{blue}[DEBUG] Mining session not started!")
            while True:
                res = await self.http(self.gamee_url, json.dumps(start_mining_data))
                if "error" in res.json().keys():
                    time.sleep(2)
                    continue
                if "miningEvent" in res.json()["result"]:
                    self.log(f"{green}[SUCCESS] Mining started successfully!")
                    return

        mining_end = mining_event["miningSessionEnded"]
        mining_earnings = self.convert_token_value(mining_event["currentSessionMicroToken"])
        mining_progress = self.convert_token_value(mining_event["currentSessionMicroTokenMined"])
        total_mined = self.convert_token_value(mining_event["cumulativeMicroTokenMined"])
        self.log(f"{green}Total mined: {total_mined}")
        self.log(f"{green}Max mining possible: {mining_earnings}")
        self.log(f"{green}Current mining: {mining_progress}")
        if mining_end:
            self.log(f"{blue}[DEBUG] Mining session has ended!")
            while True:
                res = await self.http(self.gamee_url, json.dumps(start_mining_data))
                result = res.json().get("result")
                error = res.json().get("error")
                if error is not None:
                    msg = error.get("message").lower()
                    if msg == "mining session in progress.":
                        self.log(f"{blue}[DEBUG] Mining already in progress!")
                        return
                    time.sleep(2)
                    continue
                if result.get("miningEvent") is not None:
                    self.log(f"{green}[SUCCESS] Mining started successfully!")
                    return

        self.log(f"{blue}[DEBUG] Mining is not finished yet!")
        return

    async def start(self, proxy=None):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en,id-ID;q=0.9,id;q=0.8,en-US;q=0.7",
            "client-language": "en",
            "content-type": "text/plain;charset=UTF-8",
            "Host": "api.gamee.com",
            "Origin": "https://prizes.gamee.com",
            "Referer": "https://prizes.gamee.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "X-Requested-With": "org.telegram.messenger",
        }
        if proxy is None:
            self.ses = hatetepe.AsyncClient()
        else:
            self.ses = hatetepe.AsyncClient(proxy=proxy)
            await self.check_ip()
        self.ses.headers.update(headers)
        if not os.path.exists(self.ua_file):
            async with aiofiles.open(self.ua_file, "w") as w:
                await w.write(json.dumps({}))
        if not os.path.exists(self.token_file):
            async with aiofiles.open(self.token_file, "w") as w:
                await w.write(json.dumps({}))
        if not os.path.exists(self.uuid_file):
            async with aiofiles.open(self.uuid_file, "w") as w:
                await w.write(json.dumps({}))
        async with aiofiles.open(self.ua_file) as uar:
            user_agents = json.loads(await uar.read())
        async with aiofiles.open(self.uuid_file) as uuidr:
            uuid_data = json.loads(await uuidr.read())
        async with aiofiles.open(self.token_file) as tokenr:
            token_data = json.loads(await tokenr.read())
        user_agent = user_agents.get(self.id)
        if user_agent is None:
            user_agent = UserAgent(os=["android", "ios"]).random
            user_agents[self.id] = user_agent
            async with aiofiles.open(self.ua_file, "w") as uaw:
                await uaw.write(json.dumps(user_agents, indent=4))
        uuid_str = uuid_data.get(self.id)
        if uuid_str is None:
            uuid_str = uuid.uuid4().__str__()
            uuid_data[self.id] = uuid_str
            async with aiofiles.open(self.uuid_file, "w") as uw:
                await uw.write(json.dumps(uuid_data))
        self.ses.headers["x-install-uuid"] = uuid_str
        self.ses.headers["User-Agent"] = user_agent
        token = token_data.get(self.id)
        if token is None or self.is_expired(token):
            self.log(f"{blue}[DEBUG] Token is either missing or expired!")
            token = await self.login(self.query)
            token_data[self.id] = token
            async with aiofiles.open(self.token_file, "w") as tw:
                await tw.write(json.dumps(token_data, indent=4))
        self.ses.headers["authorization"] = f"Bearer {token}"
        await self.mining()
        await self.spin()
        await self.countdown(self.config.interval)

    @staticmethod
    async def countdown(seconds):
        for i in range(seconds, 0, -1):
            minutes, secs = divmod(i, 60)
            hours, minutes = divmod(minutes, 60)
            print(f"{blue}[DEBUG] Waiting {hours:02}:{minutes:02}:{secs:02}", end="\r")
            await asyncio.sleep(1)

async def main():
    os.system("cls" if os.name == "nt" else "clear")
    print_intro()  # Display the intro banner

    arg = argparse.ArgumentParser()
    arg.add_argument("-D", "--data", default="data.txt")
    arg.add_argument("-C", "--config", default="config.json")
    arg.add_argument("-P", "--proxy", default="proxies.txt")
    args = arg.parse_args()
    if not os.path.exists(args.data):
        print(f"{red}[ERROR] File {args.data} not found!")
        exit()
    if not os.path.exists(args.config):
        print(f"{red}[ERROR] File {args.config} not found!")
        exit()
    if not os.path.exists(args.proxy):
        print(f"{red}[ERROR] File {args.proxy} not found!")
        exit()
    async with aiofiles.open(args.data) as dr:
        data_lines = await dr.read()
        data_entries = [i for i in data_lines.splitlines() if len(i) > 10]
    async with aiofiles.open(args.config) as cr:
        config_content = await cr.read()
        config_data = json.loads(config_content)
        config = Config(
            config_data.get("countdown", 300),
            config_data.get("interval", 3),
            config_data.get("use_ticket_to_spin", False),
            config_data.get("max_use_ticket_to_spin", 50),
        )
    use_proxy = False
    async with aiofiles.open(args.proxy) as pr:
        proxy_list = await pr.read()
        proxies = [i for i in proxy_list.splitlines() if len(i) > 0]
        if len(proxies) > 0:
            use_proxy = True
    GameeBot.log(f"{green}[SUCCESS] Total accounts: {len(data_entries)}")
    if len(data_entries) <= 0:
        GameeBot.log(f"{red}[ERROR] No accounts detected. Please provide your data!")
        exit()
    GameeBot.log(f"{green}[SUCCESS] Using proxy: {use_proxy}")
    
    while True:
        for idx, data in enumerate(data_entries):
            GameeBot.log(f"{green}[SUCCESS] Account number: {idx + 1}")
            if use_proxy:
                proxy = proxies[idx % len(proxies)]
            else:
                proxy = None
            await GameeBot(data, config).start(proxy)

        GameeBot.log(f"{blue}[DEBUG] Sleeping for 15 min after processing all accounts...")
        await asyncio.sleep(900)  # Sleep for 15 min

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
