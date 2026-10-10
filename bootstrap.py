import socket, sys, requests, json
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
