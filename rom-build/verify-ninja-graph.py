#!/usr/bin/env python3
"""Compare Ninja DOT dependency graphs independently of address-based node IDs."""
import collections,hashlib,json,re,sys
from pathlib import Path

node_re=re.compile(r'^"([^\"]+)" \[label=("(?:[^"\\]|\\.)*")(.*)\]$')
edge_re=re.compile(r'^"([^\"]+)" -> "([^\"]+)"(.*)$')
def read(path):
 nodes={};edges=[]
 for line in Path(path).open():
  line=line.strip();n=node_re.match(line)
  if n:nodes[n[1]]=(json.loads(n[2]),'shape=ellipse' in n[3]);continue
  e=edge_re.match(line)
  if e:edges.append((e[1],e[2],e[3].strip()))
 assert nodes and edges
 # Ninja emits sibling output edges without defining an unvisited node label.
 # Their names remain byte-for-byte in the preserved multi-output build rule.
 for x,y,attrs in edges:
  if y not in nodes:
   assert x in nodes and nodes[x][1],(x,y)
   nodes[y]=('<unvisited-sibling-output>',False)
 incoming=collections.defaultdict(list);outgoing=collections.defaultdict(list)
 direct=[]
 for x,y,attrs in edges:
  assert x in nodes and y in nodes,(x,y)
  if nodes[y][1]:incoming[y].append((nodes[x][0],attrs))
  if nodes[x][1]:outgoing[x].append((nodes[y][0],attrs))
  if not nodes[x][1] and not nodes[y][1]:direct.append((nodes[x][0],nodes[y][0],attrs))
 signatures=[]
 for key,(label,is_rule) in nodes.items():
  if is_rule:signatures.append(json.dumps([label,sorted(incoming[key]),sorted(outgoing[key])],separators=(',',':')))
 data=dict(nodes=sorted(collections.Counter(nodes.values()).items()),rules=sorted(signatures),direct=sorted(direct))
 digest=hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
 return digest,dict(nodes=len(nodes),edges=len(edges),rule_instances=len(signatures),direct_edges=len(direct))
a,ac=read(sys.argv[1]);b,bc=read(sys.argv[2]);assert a==b,(a,b,ac,bc)
print(json.dumps(dict(equivalent=True,sha256=a,counts=ac),indent=2))
