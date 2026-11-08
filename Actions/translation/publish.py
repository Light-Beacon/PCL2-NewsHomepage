"""Generate a deterministic GitHub write plan for the connected Hilda-Bot account.
The agent executes this plan through the GitHub connector; no PAT is stored locally.
"""
import argparse
import json
import subprocess
from pathlib import Path
from pipeline import ROOT, LIB


def plan(paths, branch, title):
    elements = []
    for item in paths:
        path = (ROOT/item).resolve()
        if not path.is_relative_to(LIB.resolve()) or path.suffix != '.md':
            raise ValueError('Only version Markdown files may be published')
        content = path.read_text()
        if '\nllm-transalte: true\n' not in content or '\nwip:' in content:
            raise ValueError('Apply translation packet before publishing')
        elements.append({'path':str(path.relative_to(ROOT)), 'mode':'100644','type':'blob','content':content})
    if not elements:
        raise ValueError('No translations')
    base = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    tree = subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip()
    return {'repository_full_name':'Hilda-Bot/PCL2-NewsHomepage','pr_repository_full_name':'Light-Beacon/PCL2-NewsHomepage','head':'Hilda-Bot:'+branch,'account':'Hilda-Bot','email':'bot@bugjump.net','branch':branch,'base':'main','parent_sha':base,'base_tree_sha':tree,'tree_elements':elements,'message':title,'pr_title':title,'pr_body':'以 Minecraft.net 官方更新日志为原文、中文 Minecraft Wiki 为译名参考。使用固定版本 SPXX 转换，LLM 翻译；已校验源链接和 MC 漏洞编号，移除 wip 并标记 llm-transalte: true。\n\n请人工复核译文。'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--branch',required=True)
    parser.add_argument('--title',required=True)
    parser.add_argument('paths',nargs='+')
    args = parser.parse_args()
    print(json.dumps(plan(args.paths,args.branch,args.title),ensure_ascii=False,indent=2))
