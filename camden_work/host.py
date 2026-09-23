"""Typed admission adapter configured by a trusted local operator process.

The host chooses the method from its actual receiving route. Never derive
that choice, principal, channel or grant from model text or tool output.
This is not a remote identity authenticator or a hostile-process sandbox.
"""
from dataclasses import dataclass
from .core import Node,Denied,identifier

@dataclass(frozen=True)
class LocalInputHost:
    node:Node
    principal:str
    channel:str
    grant:str
    tenant:str
    target:str

    def __post_init__(self):
        for value in (self.principal,self.channel,self.grant,self.tenant,self.target):identifier(value)

    def receive_user(self,event_id,payload):
        return self._receive('user_input',event_id,payload)

    def receive_machine(self,event_id,payload):
        return self._receive('host_machine_input',event_id,payload)

    def _receive(self,kind,event_id,payload):
        if type(payload)!=dict or set(payload)!={'delta'} or type(payload['delta'])!=int:raise Denied('HOST_INPUT_PAYLOAD')
        return self.node.admit(grant=self.grant,tenant=self.tenant,target=self.target,delta=payload['delta'],
            _host_origin={'principal':self.principal,'channel':self.channel,'event_id':identifier(event_id),'kind':kind})
