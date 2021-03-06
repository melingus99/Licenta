import asyncio
from copy import deepcopy
from selenium import webdriver
import time
from environs import Env

import constants


import config
from config import init_logging
import logging

from teams import load_team
from showdown.run_battle import pokemon_battle
from showdown.websocket_client import PSWebsocketClient

from data import all_move_json
from data import pokedex
from data.mods.apply_mods import apply_mods
from showdown.battle_bots.RL_agent.Config.config import *
from showdown.battle_bots.RL_agent.train import train

logger = logging.getLogger(__name__)


def parse_configs():
    env = Env()
    env.read_env()

    config.battle_bot_module = env("BATTLE_BOT", 'safest')
    config.save_replay = env.bool("SAVE_REPLAY", config.save_replay)
    config.use_relative_weights = env.bool("USE_RELATIVE_WEIGHTS", config.use_relative_weights)
    config.gambit_exe_path = env("GAMBIT_PATH", config.gambit_exe_path)
    config.search_depth = int(env("MAX_SEARCH_DEPTH", config.search_depth))
    config.greeting_message = env("GREETING_MESSAGE", config.greeting_message)
    config.battle_ending_message = env("BATTLE_OVER_MESSAGE", config.battle_ending_message)
    config.websocket_uri = env("WEBSOCKET_URI", "sim.smogon.com:8000")
    config.username = env("PS_USERNAME")
    config.password = env("PS_PASSWORD", "")
    config.bot_mode = env("BOT_MODE")
    config.team_name = env("TEAM_NAME", None)
    config.pokemon_mode = env("POKEMON_MODE", constants.DEFAULT_MODE)
    config.run_count = int(env("RUN_COUNT", 1))

    if config.bot_mode == constants.CHALLENGE_USER:
        config.user_to_challenge = env("USER_TO_CHALLENGE")
    init_logging(env("LOG_LEVEL", "DEBUG"))


def check_dictionaries_are_unmodified(original_pokedex, original_move_json):
    # The bot should not modify the data dictionaries
    # This is a "just-in-case" check to make sure and will stop the bot if it mutates either of them
    if original_move_json != all_move_json:
        logger.critical("Move JSON changed!\nDumping modified version to `modified_moves.json`")
        with open("modified_moves.json", 'w') as f:
            json.dump(all_move_json, f, indent=4)
        exit(1)
    else:
        logger.debug("Move JSON unmodified!")

    if original_pokedex != pokedex:
        logger.critical("Pokedex JSON changed!\nDumping modified version to `modified_pokedex.json`")
        with open("modified_pokedex.json", 'w') as f:
            json.dump(pokedex, f, indent=4)
        exit(1)
    else:
        logger.debug("Pokedex JSON unmodified!")

def login_browser(driver,username,password):


    while(True):
        try:
            login_button=driver.find_element_by_name('login')
            login_button.click()
            break
        except:
            time.sleep(0.1)


    username_driver=driver.find_element_by_name('username')
    username_driver.send_keys(username)

    div=driver.find_element_by_class_name("ps-popup")
    login_button=div.find_elements_by_tag_name('button')
    for button in login_button:
        if button.text=='Choose name':
            button.click()
            break
    while(True):
        try:
            password_driver=driver.find_element_by_name('password')
            password_driver.send_keys(password)
            break
        except:
            time.sleep(0.1)

    login_button=driver.find_elements_by_tag_name('button')
    for button in login_button:
        if button.text=='Log in':
            button.click()
            break

async def showdown(fn=None):
    parse_configs()

    apply_mods(config.pokemon_mode)

    original_pokedex = deepcopy(pokedex)
    original_move_json = deepcopy(all_move_json)

    driver = webdriver.Chrome()
    driver.get('https://play.pokemonshowdown.com/')
    login_browser(driver,config.username,config.password)

    ps_websocket_client = await PSWebsocketClient.create(config.username, config.password, config.websocket_uri)
    await ps_websocket_client.login()

    battles_run = 0
    wins = 0
    losses = 0
    while True:
        team = load_team(config.team_name)
        if config.bot_mode == constants.CHALLENGE_USER:
            await ps_websocket_client.challenge_user(config.user_to_challenge, config.pokemon_mode, team)
        elif config.bot_mode == constants.ACCEPT_CHALLENGE:
            await ps_websocket_client.accept_challenge(config.pokemon_mode, team)
        elif config.bot_mode == constants.SEARCH_LADDER:
            await ps_websocket_client.search_for_match(config.pokemon_mode, team)
        else:
            raise ValueError("Invalid Bot Mode")

        winner = await pokemon_battle(ps_websocket_client, config.pokemon_mode)

        if winner == config.username:
            wins += 1
        else:
            losses += 1

        logger.info("W: {}\tL: {}".format(wins, losses))


        check_dictionaries_are_unmodified(original_pokedex, original_move_json)

        if train_in_place==True:
            train()
            print('train completed')

        battles_run += 1
        fn(battles_run)
        if battles_run >= config.run_count:
            # driver.close()
            break



if __name__ == "__main__":
    loop=asyncio.get_event_loop()
    try:
        loop.run_until_complete(showdown())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
