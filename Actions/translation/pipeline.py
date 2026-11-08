"""Prepare immutable translation packets; apply reviewed translations. No LLM API key needed."""
import argparse
import hashlib
import json
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / 'Project/libraries/Versions'
WORK = ROOT / '.translation-work'
SPXX_SHA = '6dde210a147062c565fae8f1b747e334f9f8f751'
MANIFEST = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'PCL2-NewsHomepage-Translation/1.0 (bot@bugjump.net)'})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read().decode('utf-8')


def version_info(vid):
    if re.fullmatch(r'\d+(?:\.\d+){1,2}', vid):
        base, kind, slug = vid, 'release', 'java-edition-' + vid.replace('.', '-')
    elif m := re.fullmatch(r'(\d+(?:\.\d+)+)-(snapshot|pre|rc)-?(\d+)', vid):
        base, short, index = m.groups()
        kind = {'snapshot':'snapshot','pre':'pre-release','rc':'release-candidate'}[short]
        slug = base.replace('.', '-') + '-' + kind + '-' + index
    else:
        raise ValueError(f'Unsupported version: {vid}; explicit path mapping required')
    major = '.'.join(base.split('.')[:2]) if base.startswith('1.') else base.split('.')[0]
    return Path(major) / base / kind / (vid + '.md'), 'https://www.minecraft.net/en-us/article/minecraft-' + slug


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def sync_after_detection():
    """Fast-forward only; never discard local changes or merge divergent work."""
    dirty = subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT, text=True)
    if dirty.strip():
        raise RuntimeError('Tracked local changes exist; use a clean checkout before pulling')
    subprocess.run(['git', 'pull', '--ff-only',
                    'https://github.com/Light-Beacon/PCL2-NewsHomepage.git', 'main'],
                   cwd=ROOT, check=True)


def prepare(days):
    WORK.mkdir(exist_ok=True)
    manifest = json.loads(fetch(MANIFEST))
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    # Detect first, then pull before reading targets or preparing source packets.
    pending = False
    for v in manifest['versions']:
        if datetime.fromisoformat(v['releaseTime'].replace('Z','+00:00')) < cutoff:
            continue
        if v['type'] not in ('release', 'snapshot'):
            continue
        try:
            relative, _ = version_info(v['id'])
        except ValueError:
            continue
        target = LIB / relative
        if not target.exists() or re.search(r'^wip:\s*true\s*$', target.read_text(), re.M):
            pending = True
            break
    if pending:
        sync_after_detection()
    packets, failures = [], []
    for v in manifest['versions']:
        if datetime.fromisoformat(v['releaseTime'].replace('Z','+00:00')) < cutoff:
            continue
        if v['type'] not in ('release','snapshot'):
            continue
        vid = v['id']
        try:
            relative, official = version_info(vid)
            target = LIB / relative
            old = target.read_text() if target.exists() else ''
            if old and not re.search(r'^wip:\s*true\s*$', old, re.M):
                continue  # Never overwrite existing completed/manual translations.
            folder = WORK / vid
            folder.mkdir(exist_ok=True)
            html = fetch(official)
            (folder/'official.html').write_text(html)
            source = WORK/'spxx'
            if not source.exists():
                subprocess.run(['git','clone','https://github.com/Light-Beacon/SpxxNhpOptimized.git',str(source)],check=True)
            subprocess.run(['git','-C',str(source),'checkout','--detach',SPXX_SHA],check=True)
            subprocess.run(['node',str(Path(__file__).with_name('convert.mjs')),str(source),str(folder/'official.html'),official,str(folder/'source.md')],check=True)
            title = 'Java版' + vid
            api = 'https://zh.minecraft.wiki/api.php?' + urllib.parse.urlencode({'action':'parse','page':title,'prop':'wikitext','format':'json','redirects':1})
            wiki = json.loads(fetch(api))
            if 'error' in wiki:
                raise RuntimeError('Chinese Wiki page unavailable; retry next run')
            (folder/'wiki.json').write_text(json.dumps(wiki,ensure_ascii=False,indent=2))
            details = json.loads(fetch(v['url']))
            metadata = {'version':vid,'path':str(target.relative_to(ROOT)),'original_sha256':digest(old),'official_url':official,'wiki_url':'https://zh.minecraft.wiki/w/'+urllib.parse.quote(title),'wiki_revision':wiki['parse'].get('revid'),'server_jar':details.get('downloads',{}).get('server',{}).get('url'),'spxx_commit':SPXX_SHA}
            (folder/'packet.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
            packets.append(str(folder/'packet.json'))
        except Exception as exc:
            failures.append({'version':vid,'error':str(exc)})
    result = {'packets':packets,'failures':failures}
    (WORK/'queue.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if failures:
        raise SystemExit(1)


def apply(packet, translation):
    meta = json.loads(packet.read_text())
    target = (ROOT/meta['path']).resolve()
    if not target.is_relative_to(LIB.resolve()) or target.suffix != '.md':
        raise ValueError('Invalid target')
    old = target.read_text() if target.exists() else ''
    if digest(old) != meta['original_sha256']:
        raise ValueError('Target changed since preparation; prepare again')
    body = translation.read_text().strip()
    source = packet.with_name('source.md').read_text()
    if len(body) < 200 or not re.search(r'[\u4e00-\u9fff]',body) or body.startswith('---'):
        raise ValueError('Expected Chinese Markdown body without front matter')
    if set(re.findall(r'MC-\d+',source)) - set(re.findall(r'MC-\d+',body)):
        raise ValueError('Missing bug IDs')
    if set(re.findall(r'https?://[^\s)<>]+',source)) - set(re.findall(r'https?://[^\s)<>]+',body)):
        raise ValueError('Missing source links')
    if old:
        m = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)',old,re.S)
        if not m:
            raise ValueError('Malformed front matter')
        header = re.sub(r'^(?:wip|llm-transalte):[^\n]*(?:\n|$)','',m[1],flags=re.M).rstrip()
    else:
        header = 'version-image-link: null\nserver-jar: '+json.dumps(meta['server_jar'])+'\ntranslator: Hilda-Bot\ncats: '+json.dumps([target.parent.parent.name])
    content = '---\n'+header+'\nllm-transalte: true\n---\n'+body+'\n\n'
    content += f"<!-- 原文：{meta['official_url']}；译名参考：{meta['wiki_url']}（revision {meta['wiki_revision']}）；SPXX {SPXX_SHA} -->\n"
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary = target.with_suffix('.md.tmp')
    temporary.write_text(content)
    temporary.replace(target)
    print(target.relative_to(ROOT))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    p = sub.add_parser('prepare'); p.add_argument('--days',type=int,default=14)
    p = sub.add_parser('apply'); p.add_argument('packet',type=Path); p.add_argument('translation',type=Path)
    args = parser.parse_args()
    if args.command == 'prepare': prepare(args.days)
    else: apply(args.packet,args.translation)
