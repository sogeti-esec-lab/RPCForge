from rpc_forge import *
class Struct_40_t(NdrStructure):
    MEMBERS = [NdrLong, NdrLong, ]

class Struct_48_t(NdrStructure):
    MEMBERS = [NdrLong, Struct_40_t, Struct_40_t, Struct_40_t, ]

class Struct_170_t(NdrStructure):
    MEMBERS = [NdrLong, NdrLong, Struct_48_t, ]

class Union_24_t(NdrUnion):
    SWITCHTYPE = NdrLong
    MEMBERS = {1: NdrUniquePTR(Struct_48_t), }


class Union_80_t(NdrUnion):
    SWITCHTYPE = NdrLong
    MEMBERS = {1: NdrLong, }


class Union_144_t(NdrUnion):
    SWITCHTYPE = NdrLong
    MEMBERS = {1: NdrUniquePTR(NdrWString), 2: NdrUniquePTR(Struct_170_t), }


class Struct_190_t(NdrStructure):
    MEMBERS = [NdrHyper, ]


interface = Interface("3a9ef155-691d-4449-8d05-09ad57031823", (1,0), [

Method("I_pSchRpcRegisterTask", 1, 
In(NdrLong), 
In(NdrWString), 
In(NdrWString), 
In(NdrLong), 
In(NdrUniquePTR(NdrWString)), 
In(NdrUniquePTR(NdrWString)), 
In(SwitchIs(1) / Union_24_t)),

Method("I_pSchRpcEnumTasks", 1, 
In(NdrLong), 
In(SwitchIs(1) / Union_80_t), 
In(Out(NdrLong)), 
In(NdrLong), 
Out(NdrLong), 
Out(NdrRef(NdrWString))),

Method("I_pSchRpcGetTaskInfo", 1, 
In(NdrLong), 
In(NdrWString), 
Out(SwitchIs(1) / Union_144_t)),

Method("I_pSchRpcAquireTaskStateNotificationsName", 1, 
In(NdrWString), 
Out(NdrRef(Struct_190_t))),

Method("I_pAcquireBackgroundExecutionMode", 1, 
In(NdrLong), 
In(NdrLong), 
Out(NdrContextHandle)),

Method("I_pReleaseBackgroundExecutionMode", 0, 
In(Out(NdrContextHandle))),

Method("I_pSetTaskDisabledForCurrentUser", 1, 
In(NdrWString), 
In(NdrSmall)),
]) 

interface.is_registered = True

interface.endpoints = []
interface.endpoints.append("ubpmtaskhostchannel")
