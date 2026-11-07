#!/usr/bin/env python3
"""Install an approved OpenRouter key through OpenCode's native credential API."""

import argparse
import json
import os
from pathlib import Path
import stat
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--key-file", required=True, type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent
binding = json.loads((root / ".uniac/deploy.json").read_text())
if stat.S_IMODE(args.key_file.stat().st_mode) != 0o600:
    parser.error("key file must be mode 0600")
key = args.key_file.read_text().strip()
if not key:
    parser.error("key file is empty")
environment = {**os.environ, "UNIAC_PLATFORM_URL": binding["platform_url"]}
environment.pop("UNIAC_PROJECT_URL", None)
print(f"Target {binding['project_name']} ({binding['project_slug']}) on {binding['platform_url']}", flush=True)
subprocess.run(["uniac", "status", "opencode"], cwd=root, env=environment, check=True)

# The key crosses exec's stdin and the loopback API, never a command argument.
remote = r'''
import base64, json, sys, urllib.request, urllib.error
from pathlib import Path
key = sys.stdin.read().strip()
password = Path('/data/server-password').read_text().strip()
authorization = 'Basic ' + base64.b64encode(('opencode:' + password).encode()).decode()
def request(method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request('http://127.0.0.1:4096' + path, data=data,
        headers={'Authorization':authorization, 'Content-Type':'application/json'}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        raise SystemExit('Native credential API refused request: HTTP ' + str(error.code))
stored = request('GET', '/api/credential')['data']
same = next((item for item in stored if item['integrationID'] == 'openrouter'
    and item['value'].get('type') == 'key' and item['value'].get('key') == key), None)
if same:
    if not same['active']:
        request('POST', '/api/credential/' + same['id'] + '/activate')
    credential = same
else:
    credential = request('POST', '/api/credential', {
        'integrationID':'openrouter', 'label':'Approved deployment OpenRouter key',
        'value':{'type':'key', 'key':key}, 'activate':True})['data']
print(json.dumps({'integration_id':'openrouter', 'credential_id':credential['id'],
    'active':True, 'storage':'native persistent credential store'}))
'''
subprocess.run(
    ["uniac", "exec", "-i", "opencode", "--", "python3", "-c", remote],
    input=key,
    text=True,
    cwd=root,
    env=environment,
    check=True,
)
