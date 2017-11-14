from rpc_forge import *

interface = Interface("0767a036-0d22-48aa-ba69-b619480f38cb", (1,0), [

Method("RAiMonitorProcess", 1, 
In(NdrLong), 
In(NdrLong), 
In(NdrUniquePTR(NdrWString)), 
In(NdrUniquePTR(NdrWString)), 
In(NdrUniquePTR(NdrWString)), 
In(NdrLong)),

Method("RAiSendToService", 1, 
In(SizeIs(2) / NdrByte), 
In(NdrLong)),

Method("RAiNotifyMsiInstall", 1, 
In(NdrUniquePTR(NdrWString)), 
In(NdrUniquePTR(NdrWString)), 
In(NdrUniquePTR(NdrWString)), 
In(NdrLong), 
In(NdrLong)),

Method("RAiLinkChildToParent", 1, 
In(NdrLong), 
In(NdrLong)),

Method("RAiGetFileInfoFromPath", 0, 
Out(Range(260,260) / NdrWString), 
Out(Range(260,260) / NdrWString), 
Out(Range(260,260) / NdrWString), 
Out(Range(260,260) / NdrWString), 
Out(Range(260,260) / NdrWString), 
Out(Range(260,260) / NdrWString), 
In(NdrUniquePTR(NdrWString))),
]) 

interface.is_registered = True

interface.endpoints = []
