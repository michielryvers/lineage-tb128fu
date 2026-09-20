#!/usr/bin/env python3
"""Build explicit Android targets through a verified reduced Ninja graph.

Run inside the usual bounded build container after Soong/Kati generation.
This preserves Siso's existing incremental state and the recorded Ninja env.
"""
import argparse,json,os,re,subprocess,sys,time
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--label',required=True)
p.add_argument('targets',nargs='+')
a=p.parse_args()
assert re.fullmatch(r'[a-zA-Z0-9_-]+',a.label)
recipe=Path(__file__).resolve().parent
root=Path.cwd();destination='out/reduced/'+a.label
evidence=root/'out/reduced'/('evidence-'+a.label);evidence.mkdir(parents=True,exist_ok=True)
ninja='prebuilts/build-tools/linux-x86/bin/ninja'
original='out/combined-lineage_tb128fu.ninja';reduced=destination+'/'+original
def run(args,output):
 print(time.strftime('%Y-%m-%d %H:%M:%S'), ' '.join(map(str,args)),flush=True)
 with output.open('w') as f:subprocess.run(list(map(str,args)),check=True,stdout=f)
run([ninja,'-f',original,'-t','graph',*a.targets],evidence/'original.dot')
run([sys.executable,recipe/'reduce-ninja.py','--source-root',root,'--graph',evidence/'original.dot','--destination',destination],evidence/'reduction.json')
run([ninja,'-f',reduced,'-t','graph',*a.targets],evidence/'reduced.dot')
run([sys.executable,recipe/'verify-ninja-graph.py',evidence/'original.dot',evidence/'reduced.dot'],evidence/'equivalence.json')
# Lineage's kernel makefile uses the host's online CPU count independently of
# Ninja's job limit. Cap only that nested make command in the reduced copy.
# Dependencies and original generated files remain untouched.
kati=root/destination/'out/build-lineage_tb128fu.ninja'
temporary=kati.with_suffix('.ninja.jobs-tmp')
changes=[]
with kati.open() as source, temporary.open('w') as output:
 for number,line in enumerate(source,1):
  if line.lstrip().startswith('command =') and '/KERNEL_OBJ' in line:
   updated,count=re.subn(r'(/bin/make\s+)-j[0-9]+\b',r'\g<1>-j1',line)
   if count:
    changes.append({'line':number,'nested_make_commands':count})
    line=updated
  output.write(line)
temporary.replace(kati)
(evidence/'kernel-job-limit.json').write_text(json.dumps({'jobs':1,'changes':changes},indent=2)+'\n')
env={row['Key']:row['Value'] for row in json.loads(Path('out/soong/ninja.environment').read_text())}
env.update(GOMEMLIMIT='6GiB',GOGC='25')
args=['prebuilts/siso/linux-x86/siso','--log_dir','out','ninja','-d','keepdepfile','-d','keeprsp','--local_jobs','1','--log_dir','out','--config_repo_dir=out/siso_config','--state_dir','out','-f',reduced,*a.targets]
print('Dependency equivalence passed; compiling with one local job.',flush=True)
subprocess.run(args,env=env,check=True)
