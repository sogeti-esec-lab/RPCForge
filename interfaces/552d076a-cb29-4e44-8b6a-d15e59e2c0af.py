from rpc_forge import *

interface = Interface("552d076a-cb29-4e44-8b6a-d15e59e2c0af", (1,0), [

Method("IpTransitionProtocolApplyConfigChanges", 1, 
In(NdrByte)),

Method("IpTransitionProtocolApplyConfigChangesEx", 1, 
In(NdrByte), 
In(Range(0,65535) / NdrLong), 
In(SizeIs(2) / NdrByte)),
]) 

interface.is_registered = True

interface.endpoints = []
interface.endpoints.append("TeredoDiagnostics")
