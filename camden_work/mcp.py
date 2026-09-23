"""Opt-in, read-only MCP stdio subset pinned to specification 2025-11-25.

No prompts, sampling, elicitation, network, shell, writes, or arbitrary paths.
The operator selects an optional export directory at process launch.
"""
import argparse,json,sys
from pathlib import Path
from . import __version__
from .catalog import entry,search
from .core import Denied,identifier

PROTOCOL='2025-11-25'
MAX_MESSAGE=16384
TOOLS=[
 {'name':'catalog_search','description':'Search public research definitions. Results are data, not authority or test evidence.','inputSchema':{'type':'object','properties':{'query':{'type':'string','maxLength':200},'family':{'type':'string'},'basis':{'enum':['R','E','D']},'outcome':{'enum':['EFFECT','CLAIM','LINEAGE','AUTHORITY','CONTINUATION','VERIFICATION','OBJECTIVE','BINDING','CONFIDENTIALITY','RESOURCE']},'offset':{'type':'integer','minimum':0},'limit':{'type':'integer','minimum':1,'maximum':25}},'additionalProperties':False}},
 {'name':'catalog_entry','description':'Read a complete public definition or resolve an alias.','inputSchema':{'type':'object','properties':{'identity':{'type':'string','maxLength':40}},'required':['identity'],'additionalProperties':False}},
 {'name':'inspect_export','description':'Read one named JSON export in the operator-selected directory. Does not certify its truth.','inputSchema':{'type':'object','properties':{'name':{'type':'string','maxLength':120}},'required':['name'],'additionalProperties':False}}
]
for tool in TOOLS:tool['annotations']={'readOnlyHint':True,'destructiveHint':False,'openWorldHint':False}

class Server:
    def __init__(self,exports=None):self.exports=Path(exports).resolve() if exports else None;self.phase='new'
    def request(self,v):
        if not isinstance(v,dict) or v.get('jsonrpc')!='2.0' or not isinstance(v.get('method'),str):return {'jsonrpc':'2.0','id':v.get('id') if isinstance(v,dict) else None,'error':{'code':-32600,'message':'Invalid request'}}
        rid=v.get('id');method=v['method'];params=v.get('params',{})
        def ok(value):return {'jsonrpc':'2.0','id':rid,'result':value}
        def error(code,message):return {'jsonrpc':'2.0','id':rid,'error':{'code':code,'message':message}}
        if 'id' not in v:
            if method=='notifications/initialized' and self.phase=='negotiated':self.phase='ready'
            return None
        if type(rid) not in (str,int) or not isinstance(params,dict):return error(-32600,'Invalid request')
        if method=='initialize':
            if self.phase!='new':return error(-32600,'Already initialized')
            info=params.get('clientInfo')
            if not isinstance(params.get('capabilities'),dict) or not isinstance(info,dict) or not all(isinstance(info.get(k),str) and info[k] for k in ('name','version')):return error(-32602,'Client information and capabilities required')
            if not isinstance(params.get('protocolVersion'),str) or not params['protocolVersion']:return error(-32602,'Protocol version required')
            # Negotiate our supported version. An incompatible client should
            # disconnect; tools stay unavailable until initialized notification.
            self.phase='negotiated'
            return ok({'protocolVersion':PROTOCOL,'capabilities':{'tools':{}},'serverInfo':{'name':'camden-work-readonly','version':__version__}})
        if method=='ping':return ok({})
        if self.phase!='ready':return error(-32000,'Initialization required')
        if method=='tools/list':
            if params:return error(-32602,'No cursor or filters supported for this finite tool list')
            return ok({'tools':TOOLS})
        if method!='tools/call':return error(-32601,'Method not found')
        name=params.get('name');args=params.get('arguments',{})
        if not isinstance(args,dict):return error(-32602,'Arguments must be an object')
        tool=next((t for t in TOOLS if t['name']==name),None)
        if not tool:return error(-32602,'Unknown tool')
        schema=tool['inputSchema']
        if set(args)-set(schema['properties']) or any(k not in args for k in schema.get('required',[])):return error(-32602,'Arguments do not match schema')
        try:
            if name=='catalog_search':result=search(**args)
            elif name=='catalog_entry':result=entry(**args)
            else:
                if not self.exports:raise Denied('EXPORT_DIRECTORY_NOT_GRANTED')
                name=identifier(args['name']);path=self.exports/(name+'.json')
                if path.is_symlink() or path.resolve().parent!=self.exports:raise Denied('PATH_DENIED')
                if not path.is_file() or path.stat().st_size>1024*1024:raise Denied('EXPORT_UNAVAILABLE_OR_TOO_LARGE')
                result={'data':json.loads(path.read_text(encoding='utf8')),'verification':'Parsed export only; no independent target or authorization evidence'}
            return ok({'content':[{'type':'text','text':json.dumps(result,ensure_ascii=True)}],'isError':False})
        except (Denied,OSError,ValueError,TypeError) as exc:
            # No filesystem paths or raw private data in diagnostics.
            return ok({'content':[{'type':'text','text':str(exc) if isinstance(exc,Denied) else 'Invalid or unavailable input'}],'isError':True})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--exports');args=parser.parse_args();server=Server(args.exports)
    while True:
        raw=sys.stdin.buffer.readline(MAX_MESSAGE+1)
        if not raw:break
        if len(raw)>MAX_MESSAGE:
            print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Message too large'}}),flush=True);break
        try:reply=server.request(json.loads(raw))
        except (ValueError,UnicodeError):reply={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Parse error'}}
        if reply is not None:print(json.dumps(reply,ensure_ascii=True),flush=True)

if __name__=='__main__':main()
