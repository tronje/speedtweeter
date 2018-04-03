#!/usr/bin/env python

import configparser
import speedtest
import sys
import time
import tweepy

from typing import Dict


class ConfigError(Exception):
    pass


def parse_config():
    cfg = configparser.ConfigParser()
    cfg.read('config.ini')

    monitor = cfg['monitor']
    twitter = cfg['twitter']

    interval = int(monitor.get('interval', 600))
    tweet = monitor.getboolean('tweet', False)

    consumer_key = twitter.get('consumer_key')
    consumer_secret = twitter.get('consumer_secret')
    access_token = twitter.get('access_token')
    access_token_secret = twitter.get('access_token_secret')

    if None in [
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret
    ]:
        raise ConfigError("Missing API options!")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    return {
        'interval': interval,
        'tweet': tweet,
        'api': tweepy.API(auth)
    }


def run_test() -> Dict[str, int]:
    spdtst = speedtest.Speedtest()
    spdtst.get_best_server()

    down = spdtst.download()
    up = spdtst.upload()

    down_mb = int(down / 1_000_000)
    up_mb = int(up / 1_000_000)

    return {'down': down_mb, 'up': up_mb}


def monitor(config):
    # CSV header
    print("time,down,up")

    while True:
        results = run_test()

        print(time.strftime("%Y-%m-%d"), end=',')
        print(results['down'], end=',')
        print(results['up'])

        if config['tweet'] and results['down'] < 10:
            tweet(results, config['api'])

        time.sleep(config['interval'])


def tweet(speeds, api):
    speed_str = f"{speeds['down']} down/{speeds['up']} up"
    status = ("Hey @vodafone_de, warum ist mein Internet gerade bei "
              f"{speed_str} wenn ich für 50 down/10 up zahle?"
              )

    api.update_status(status)
    print("Tweeted to Vodafone!", file=sys.stderr)


if __name__ == "__main__":
    config = parse_config()
    monitor(config)
