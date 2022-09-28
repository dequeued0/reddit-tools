#!/usr/bin/env python3

import argparse
import json
import logging
import os
import praw
import sys
import time


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(funcName)s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
)


def clean(stuff: dict) -> dict:
    cleaned = {}
    for key, value in stuff.items():
        if isinstance(value, str):
            cleaned.update({key: value.encode('utf-16', 'surrogatepass').decode('utf-16').encode('unicode-escape').decode('ASCII')})
        else:
            cleaned.update({key: value})
    return cleaned


def read_logs(subreddit, action=None, mod=None, days=None, unicode=False):
    try:
        for log in subreddit.mod.log(limit=None, action=action, mod=mod):
            if args.days and log.created_utc < time.time() - 86400*args.days:
                break
            newlog = {key: value for key, value in log.__dict__.items() if str(type(value)).find("class 'praw") == -1}
            newlog["mod"] = newlog.pop("_mod")
            if unicode:
                print(json.dumps(clean(newlog)))
            else:
                print(json.dumps(newlog))
    except Exception as e:
        logging.error(f"unable to read logs for /r/{subreddit}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', type=str, default=None, help='action to fetch (default is all)')
    parser.add_argument('--days', type=float, default=None, help='number of days to fetch')
    parser.add_argument('--mod', type=str, default=None, help='moderator to fetch (default is all)')
    parser.add_argument('--site', type=str, default=None, help='set praw.ini site name for initialization')
    parser.add_argument('--unicode', action='store_true', help='print Unicode escapes for strings')
    parser.add_argument('subreddits', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    try:
        site_name = args.site if args.site else os.environ.get('REDDIT_SCRIPTS', None)
        r = praw.Reddit(site_name)
        for subreddit in args.subreddits:
            read_logs(r.subreddit(subreddit), action=args.action, mod=args.mod, days=args.days, unicode=args.unicode)
    except KeyboardInterrupt:
        logging.error("received SIGINT from keyboard, stopping")
        sys.exit(1)
    except Exception as e:
        logging.error(f"site error: {e}")
        sys.exit(1)
