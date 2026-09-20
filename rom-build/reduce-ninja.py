#!/usr/bin/env python3
"""Copy the exact target closure from an authoritative Ninja -t graph export.

Original generated files are never modified. Preserve selected build statements,
rules, variable bindings, pools and subninja scopes verbatim. Explicit targets
are required when invoking the resulting graph. Verify the resulting DOT graph
against the original before using it for compilation.
"""
import argparse, json, re
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--source-root',type=Path,required=True)
p.add_argument('--graph',type=Path,required=True)
p.add_argument('--destination',required=True)
p.add_argument('--root-ninja',default='out/combined-lineage_tb128fu.ninja')
a=p.parse_args()
needed=set();rules={'phony'}
node=re.compile(r'^"[^\"]+" \[label=("(?:[^"\\]|\\.)*")(.*)\]$')
for line in a.graph.open():
 m=node.match(line.strip())
 if m:
  label=json.loads(m[1])
  (rules if 'shape=ellipse' in m[2] else needed).add(label)
 elif ' -> ' in line and '[label=' in line:
  rules.add(json.loads(line[line.index('[label=')+7:line.rindex(']')]).strip())
assert needed and len(rules)>1

def statements(path):
 raw=[];logical='';block=[];head=None
 with path.open() as f:
  for line in f:
   raw.append(line)
   continuation=(len(line.rstrip('\n'))-len(line.rstrip('\n').rstrip('$')))%2==1
   logical+=line.rstrip('\n')[:-1] if continuation else line.rstrip('\n')
   if continuation:continue
   current=''.join(raw);raw=[]
   if logical and not logical[0].isspace() and not logical.startswith('#'):
    if block:yield head,''.join(block)
    head=logical;block=[current]
   else:
    block.append(current)
   logical=''
  assert not raw,'Unterminated continuation'
  if block:yield head,''.join(block)

var=re.compile(r'\$(?:\{([^}]+)\}|([a-zA-Z0-9_.-]+)|(.))')
def expand(s,env):
 def replace(m):
  name=m[1] or m[2]
  if name:
   assert name in env,('Unknown path variable',name)
   return env[name]
  assert m[3] in '$ :',('Unsupported escape',m[3])
  return m[3]
 return var.sub(replace,s)

stats=[]
def convert(name,env):
 src=a.source_root/name;dst=a.source_root/a.destination/name
 dst.parent.mkdir(parents=True,exist_ok=True)
 kept=total=0
 with dst.open('w') as out:
  for header,raw in statements(src):
   if header is None:continue
   if header.startswith('build '):
    total+=1
    # Generated output paths contain no variable/escaped space/colon forms.
    # Fail closed instead of silently emitting an incomplete dependency graph.
    outputs=header[6:].split(':',1)[0]
    assert '$' not in outputs,('Nonliteral generated output',outputs[:200])
    if any(x in needed for x in outputs.split() if x!='|'):
     kept+=1;out.write(raw)
   elif header.startswith('rule '):
    if header[5:].strip() in rules:out.write(raw)
   elif header.startswith(('subninja ','include ')):
    directive,target=header.split(None,1);target=expand(target,env)
    convert(target,env.copy() if directive=='subninja' else env)
    out.write(directive+' '+a.destination+'/'+target+'\n')
   elif header.startswith('default '):
    continue
   else:
    out.write(raw)
    if not header.startswith('pool ') and '=' in header:
     key,value=header.split('=',1)
     # Most command-only globals are not needed to resolve include paths.
     try:env[key.strip()]=expand(value.strip(),env)
     except AssertionError:pass
 stats.append(dict(file=name,edges=total,selected=kept,source_bytes=src.stat().st_size,result_bytes=dst.stat().st_size))
convert(a.root_ninja,{})
report=dict(graph=str(a.graph),nodes=len(needed),rules=len(rules),files=stats)
(a.source_root/a.destination/'reduction.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
