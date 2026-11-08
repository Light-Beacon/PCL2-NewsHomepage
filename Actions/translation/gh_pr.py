"""Create a pull request from the bot fork using GitHub CLI."""
import argparse
import json
import subprocess
from pathlib import Path

UPSTREAM = 'Light-Beacon/PCL2-NewsHomepage'
BOT = 'Hilda-Bot'


def create_pr(branch, title, body_file):
    login = subprocess.check_output(['gh', 'api', 'user', '--jq', '.login'], text=True, timeout=60).strip()
    if login.casefold() != BOT.casefold():
        raise RuntimeError(f'gh must authenticate as {BOT}; current account: {login}')
    head = f'{BOT}:{branch}'
    existing = json.loads(subprocess.check_output([
        'gh', 'pr', 'list', '--repo', UPSTREAM, '--state', 'all',
        '--head', branch, '--base', 'main', '--limit', '1000',
        '--json', 'url,state,headRepositoryOwner'], text=True, timeout=60))
    matches = [pr for pr in existing
               if pr.get('headRepositoryOwner', {}).get('login', '').casefold() == BOT.casefold()]
    if matches:
        # Do not silently reopen rejected or merged contributions.
        print(matches[0]['url'])
        return matches[0]['url']
    return subprocess.check_output([
        'gh', 'pr', 'create', '--repo', UPSTREAM, '--base', 'main',
        '--head', head, '--title', title, '--body-file', str(body_file.resolve())
    ], text=True, timeout=60).strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--branch', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--body-file', required=True, type=Path)
    args = parser.parse_args()
    print(create_pr(args.branch, args.title, args.body_file))
