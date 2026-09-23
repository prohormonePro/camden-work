"""Operator commands for the local, offline synthetic target."""
import argparse,json,sys
from .core import Node,Denied

def main(argv=None):
    p=argparse.ArgumentParser(description='Offline synthetic work continuity. No network or model calls.')
    p.add_argument('--workspace',required=True)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('init')
    sub.add_parser('challenge')
    g=sub.add_parser('grant');g.add_argument('--tenant',required=True);g.add_argument('--target',required=True);g.add_argument('--max-effects',type=int,default=10);g.add_argument('--lifetime',type=int,default=3600)
    a=sub.add_parser('admit');a.add_argument('--grant',required=True);a.add_argument('--tenant',required=True);a.add_argument('--target',required=True);a.add_argument('--delta',required=True,type=int);a.add_argument('--dependency',action='append',default=[]);a.add_argument('--profile',choices=['local-atomic','opaque'],default='local-atomic')
    a.add_argument('--expected-version',type=int);a.add_argument('--compensates')
    c=sub.add_parser('claim');c.add_argument('--worker',required=True);c.add_argument('--expected-epoch',required=True,type=int)
    s=sub.add_parser('stop');s.add_argument('--expected-epoch',required=True,type=int)
    r=sub.add_parser('revoke');r.add_argument('--grant',required=True)
    cancel=sub.add_parser('cancel');cancel.add_argument('--work',required=True)
    for name in ['execute','reconcile','verify','recover-local']:
        q=sub.add_parser(name);q.add_argument('--work',required=True);q.add_argument('--worker',required=True);q.add_argument('--epoch',required=True,type=int)
        if name=='execute':q.add_argument('--crash',choices=['after-intent','after-target'])
    w=sub.add_parser('wait');w.add_argument('--work',required=True);w.add_argument('--attempts',type=int,default=3)
    v=sub.add_parser('visibility');v.add_argument('value',choices=['available','unavailable']);v.add_argument('--tenant',required=True);v.add_argument('--target',required=True)
    svc=sub.add_parser('service');svc.add_argument('--worker',required=True);svc.add_argument('--epoch',required=True,type=int)
    status=sub.add_parser('status');status.add_argument('--work')
    export=sub.add_parser('export');export.add_argument('--name',default='result')
    for name in ['adopt-result','deliver-local','finalize']:
        q=sub.add_parser(name);q.add_argument('--name',required=True);q.add_argument('--worker',required=True);q.add_argument('--epoch',required=True,type=int)
    imp=sub.add_parser('import-review');imp.add_argument('--source',required=True)
    args=p.parse_args(argv)
    try:
        if args.command=='challenge':
            from .challenge import run
            result=run(args.workspace)
        elif args.command=='init':Node.initialize(args.workspace);result={'initialized':True,'network':False,'background_service':False}
        else:
            n=Node(args.workspace)
            if args.command=='grant':result={'grant':n.grant(tenant=args.tenant,target=args.target,max_effects=args.max_effects,lifetime=args.lifetime)}
            elif args.command=='admit':result={'work':n.admit(grant=args.grant,tenant=args.tenant,target=args.target,delta=args.delta,dependencies=args.dependency,profile=args.profile,expected_version=args.expected_version,compensates=args.compensates)}
            elif args.command=='claim':result={'epoch':n.claim(args.worker,expected_epoch=args.expected_epoch)}
            elif args.command=='stop':n.stop(expected_epoch=args.expected_epoch);result={'stopped':True}
            elif args.command=='revoke':n.revoke(args.grant);result={'revoked':True}
            elif args.command=='execute':result=n.execute(args.work,worker=args.worker,epoch=args.epoch,crash=args.crash)
            elif args.command=='reconcile':result=n.reconcile(args.work,worker=args.worker,epoch=args.epoch)
            elif args.command=='verify':result=n.verify(args.work,worker=args.worker,epoch=args.epoch)
            elif args.command=='recover-local':result=n.recover_local(args.work,worker=args.worker,epoch=args.epoch)
            elif args.command=='cancel':result=n.cancel(args.work)
            elif args.command=='wait':n.wait(args.work,attempts=args.attempts);result={'registered':True,'background_wake':False,'next_action':'Invoke service after condition changes'}
            elif args.command=='visibility':n.visibility(args.value=='available',tenant=args.tenant,target=args.target);result={'available':args.value=='available'}
            elif args.command=='service':result=n.service(worker=args.worker,epoch=args.epoch)
            elif args.command=='status':result=n.status(args.work)
            elif args.command=='export':result=n.export(args.name)
            elif args.command=='adopt-result':result=n.adopt_result(args.name,worker=args.worker,epoch=args.epoch)
            elif args.command=='deliver-local':result=n.deliver_local(args.name,worker=args.worker,epoch=args.epoch)
            elif args.command=='finalize':result=n.finalize(args.name,worker=args.worker,epoch=args.epoch)
            elif args.command=='import-review':result=n.import_review(args.source)
        print(json.dumps(result,ensure_ascii=True))
    except (Denied,FileExistsError) as exc:
        print(json.dumps({'error':type(exc).__name__,'detail':str(exc)}),file=sys.stderr);raise SystemExit(2)
