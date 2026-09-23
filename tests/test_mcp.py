import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from camden_work.mcp import Server,PROTOCOL

def req(method,params=None,i=1):
    params=params or {}
    if method=='initialize':params={'capabilities':{},'clientInfo':{'name':'test-client','version':'1'},**params}
    return {'jsonrpc':'2.0','id':i,'method':method,'params':params}

class MCPTests(unittest.TestCase):
    def ready(self,exports=None):
        s=Server(exports);s.request(req('initialize',{'protocolVersion':PROTOCOL}));s.request({'jsonrpc':'2.0','method':'notifications/initialized'});return s
    def test_actual_stdio_exchange_and_reconnect(self):
        messages=[req('initialize',{'protocolVersion':PROTOCOL}),{'jsonrpc':'2.0','method':'notifications/initialized'},req('tools/list',i=2),req('tools/call',{'name':'catalog_entry','arguments':{'identity':'AF-AU-13'}},3)]
        for _ in range(2):
            r=subprocess.run([sys.executable,'-B','-m','camden_work.mcp'],input='\n'.join(json.dumps(x) for x in messages)+'\n',text=True,capture_output=True,timeout=10)
            self.assertEqual(r.returncode,0,r.stderr);out=[json.loads(x) for x in r.stdout.splitlines()]
            self.assertEqual(len(out),3);self.assertEqual(out[0]['result']['protocolVersion'],PROTOCOL)
            self.assertEqual(len(out[1]['result']['tools']),3)
            self.assertEqual(json.loads(out[2]['result']['content'][0]['text'])['canonical_id'],'AF-SE-01')
    def test_no_preinit_tool(self):self.assertIn('error',Server().request(req('tools/list')))
    def test_other_version_negotiates_supported_version_before_tools(self):
        server=Server()
        result=server.request(req('initialize',{'protocolVersion':'2024-11-05'}))
        self.assertEqual(result['result']['protocolVersion'],PROTOCOL)
        self.assertIn('error',server.request(req('tools/list',i=2)))
    def test_missing_version_rejected(self):self.assertIn('error',Server().request(req('initialize')))
    def test_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            out=self.ready(d).request(req('tools/call',{'name':'inspect_export','arguments':{'name':'../secret'}}))
            self.assertTrue(out['result']['isError'])
    def test_missing_permission(self):
        out=self.ready().request(req('tools/call',{'name':'inspect_export','arguments':{'name':'result'}}));self.assertTrue(out['result']['isError'])
    def test_bounded_search(self):
        out=self.ready().request(req('tools/call',{'name':'catalog_search','arguments':{'limit':100000}}));self.assertTrue(out['result']['isError'])
    def test_unknown_argument(self):
        out=self.ready().request(req('tools/call',{'name':'catalog_search','arguments':{'url':'https://example.com'}}));self.assertIn('error',out)
    def test_bad_json_and_oversize(self):
        for line,code in [('not-json\n',-32700),('x'*16385+'\n',-32600)]:
            r=subprocess.run([sys.executable,'-B','-m','camden_work.mcp'],input=line,text=True,capture_output=True,timeout=10)
            self.assertEqual(json.loads(r.stdout)['error']['code'],code)
    def test_export_read_not_truth(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'result.json';p.write_text('{"verified":true}',encoding='utf8');before=p.read_bytes()
            out=self.ready(d).request(req('tools/call',{'name':'inspect_export','arguments':{'name':'result'}}))
            self.assertFalse(out['result']['isError']);self.assertIn('no independent target',out['result']['content'][0]['text']);self.assertEqual(before,p.read_bytes())

if __name__=='__main__':unittest.main()
