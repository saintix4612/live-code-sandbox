#!/usr/bin/env python3
"""Exercise unmodified Sherlock against loopback-only synthetic profiles.
Run with the existing Sherlock virtualenv's Python. No real accounts searched.
This is process/network isolation for reproduction, not an OS security sandbox.
"""
import json, os, pathlib, subprocess, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = pathlib.Path(os.environ['SHERLOCK_SOURCE']).resolve()
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
requests_seen = []
class Handler(BaseHTTPRequestHandler):
    def respond(self, body=True):
        requests_seen.append({'method': self.command, 'path': self.path})
        missing = self.path.endswith('/missing_demo')
        self.send_response(404 if missing else 200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.end_headers()
        if body: self.wfile.write(b'<html>synthetic local profile</html>')
    def do_GET(self): self.respond()
    def do_HEAD(self): self.respond(False)
    def log_message(self,*args): pass
server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}'
manifest = ROOT / 'local-sites.json'
manifest.write_text(json.dumps({'Sandbox': {'urlMain':base,'url':base+'/profile/{}','username_claimed':'saved_demo','errorType':'status_code','errorCode':404,'request_method':'GET'}}),encoding='utf-8')
# Execute real upstream CLI and search/save code. Stub only update metadata;
# use a local site manifest, disable remote exclusions, block external sockets.
bootstrap = ROOT / 'bootstrap.py'
bootstrap.write_text('''import socket, sys, requests, json
from urllib.parse import urlparse
from sherlock_project import sherlock as cli
original_connect = socket.socket.connect
original_connect_ex = socket.socket.connect_ex
def guard(original):
    def connect(self,address):
        if isinstance(address,tuple) and address[0] != '127.0.0.1':
            raise RuntimeError('Sandbox blocked external socket: '+str(address))
        return original(self,address)
    return connect
socket.socket.connect = guard(original_connect)
socket.socket.connect_ex = guard(original_connect_ex)
original_get = requests.get
def local_get(url,*args,**kwargs):
    if url == cli.forge_api_latest_release:
        response = requests.Response(); response.status_code=200
        response._content=json.dumps({'tag_name':'v'+cli.__version__}).encode()
        return response
    if urlparse(url).hostname != '127.0.0.1':
        raise RuntimeError('Sandbox blocked external HTTP: '+url)
    return original_get(url,*args,**kwargs)
requests.get = local_get
cli.main()
''',encoding='utf-8')
cases = [
 ('save_txt',['--txt','saved_demo']),
 ('save_csv',['--csv','saved_demo']),
 ('save_xlsx',['--xlsx','saved_demo']),
 ('missing_profile',['--csv','missing_demo']),
 ('save_batch',['--txt','first_demo','second_demo']),
 ('slash_txt_batch',['--txt','a/b','second_demo']),
 ('slash_csv_batch',['--csv','a/b','second_demo']),
 ('slash_xlsx_batch',['--xlsx','a/b','second_demo']),
 ('missing_output_parent',['--txt','--output','nonexistent/results.txt','saved_demo']),
 ('output_is_directory',['--txt','--output','directory','saved_demo']),
 ('read_only_output',['--txt','--output','readonly/results.txt','saved_demo']),
 ('folder_is_file',['--txt','--folderoutput','blocked','first_demo','second_demo']),
]
summary = []
env = os.environ.copy()
env.update(PYTHONPATH=str(SOURCE),NO_PROXY='*',PYTHONUNBUFFERED='1')
for name,args in cases:
    case = EVIDENCE / name
    case.mkdir(exist_ok=True)
    # Each run has its own disposable output directory.
    run = case / 'saved-files'
    run.mkdir(exist_ok=True)
    if name=='output_is_directory': (run/'directory').mkdir(exist_ok=True)
    if name=='read_only_output':
        (run/'readonly').mkdir(exist_ok=True); (run/'readonly').chmod(0o500)
    if name=='folder_is_file': (run/'blocked').write_text('I am a file, not a directory.\n')
    before = len(requests_seen)
    command=[sys.executable,str(bootstrap),'--json',str(manifest),'--ignore-exclusions','--no-color','--timeout','2']+args
    try:
        result=subprocess.run(command,cwd=run,env=env,capture_output=True,text=True,timeout=20)
    finally:
        if name=='read_only_output': (run/'readonly').chmod(0o700)
    (case/'stdout.log').write_text(result.stdout,encoding='utf-8')
    (case/'stderr.log').write_text(result.stderr,encoding='utf-8')
    seen=requests_seen[before:]
    (case/'requests.json').write_text(json.dumps(seen,indent=2))
    files=[str(p.relative_to(run)) for p in run.rglob('*') if p.is_file()]
    row={'case':name,'arguments':args,'exit_code':result.returncode,'requests':seen,'saved_files':files,'error':result.stderr.strip().splitlines()[-1] if result.stderr.strip() else None}
    summary.append(row)
    print(json.dumps(row))
server.shutdown(); server.server_close()
(ROOT/'summary.json').write_text(json.dumps(summary,indent=2))
assert all(x['exit_code']==0 for x in summary[:5]),'A normal save failed'
assert all(x['exit_code']!=0 for x in summary[5:]),'An expected reproduction did not fail'
assert all(not any('second_demo' in r['path'] for r in x['requests']) for x in summary[5:8]),'Batch unexpectedly continued'
print('Verified: 5 normal runs succeeded; 7 failure cases reproduced; failed saves stopped later usernames.')
