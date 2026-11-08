"""Commit version Markdown with a configured signing key, verify, then push."""
import argparse
import subprocess
from pathlib import Path
from pipeline import ROOT, LIB


def output(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def publish(branch, message, paths):
    if output(['gh', 'api', 'user', '--jq', '.login']).casefold() != 'hilda-bot':
        raise RuntimeError('gh must authenticate as Hilda-Bot')
    if output(['git', 'branch', '--show-current']) != branch:
        raise RuntimeError('Check out the intended publishing branch first')
    # Explicit configuration prevents accidental use of the personal default key.
    if output(['git', 'config', '--local', '--get', 'user.email']) != 'bot@bugjump.net':
        raise RuntimeError('Configure repository-local bot@bugjump.net identity')
    key = output(['git', 'config', '--local', '--get', 'user.signingkey'])
    if not key:
        raise RuntimeError('Configure a repository-local Hilda-Bot signing key')
    if output(['git', 'diff', '--cached', '--name-only']):
        raise RuntimeError('Index must be empty before publishing')
    files = []
    for item in paths:
        path = (ROOT / item).resolve()
        if not path.is_relative_to(LIB.resolve()) or path.suffix != '.md':
            raise ValueError('Only version Markdown files may be published')
        content = path.read_text()
        if '\nllm-transalte: true\n' not in content or '\nwip:' in content:
            raise ValueError('Apply the translation packet first')
        files.append(str(path.relative_to(ROOT)))
    if not files:
        raise ValueError('No translations')
    subprocess.run(['git', 'add', '--', *files], cwd=ROOT, check=True)
    subprocess.run(['git', '-c', 'user.name=Hilda Bot', '-c', 'user.email=bot@bugjump.net',
                    'commit', '-S', '-m', message], cwd=ROOT, check=True)
    subprocess.run(['git', 'verify-commit', 'HEAD'], cwd=ROOT, check=True)
    subprocess.run(['git', '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential',
                    'push', 'https://github.com/Hilda-Bot/PCL2-NewsHomepage.git',
                    f'HEAD:refs/heads/{branch}'], cwd=ROOT, check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--branch', required=True)
    parser.add_argument('--message', required=True)
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    publish(args.branch, args.message, args.paths)
