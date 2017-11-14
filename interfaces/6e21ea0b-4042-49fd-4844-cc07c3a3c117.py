from rpc_forge import *
class Struct_96_t(NdrStructure):
    MEMBERS = [NdrLong, NdrShort, NdrShort, NdrByte, NdrByte, NdrByte, NdrByte, NdrByte, NdrByte, NdrByte, NdrByte, ]


interface = Interface("6e21ea0b-4042-49fd-4844-cc07c3a3c117", (1,6), [

Method("s_winmmGetPnpInfo", 0, 
Out(NdrLong), 
Out(NdrRef(SizeIs(0, 'deref') / NdrByte))),

Method("s_mmeNotifyDeviceStateChanged", 1, 
In(NdrWString), 
In(NdrLong)),

Method("s_mmeNotifyDeviceAdded", 1, 
In(NdrWString)),

Method("s_mmeNotifyDeviceRemoved", 1, 
In(NdrWString)),

Method("s_mmeNotifyDefaultDeviceChanged", 1, 
In(NdrLong), 
In(NdrLong), 
In(NdrWString)),

Method("s_tsSessionGetAudioProtocol", 1, 
In(NdrLong), 
Out(NdrLong), 
Out(NdrLong)),

Method("s_tsRegisterAudioProtocolNotification", 1, 
Out(NdrContextHandle)),

Method("s_tsUnregisterAudioProtocolNotification", 1, 
In(Out(NdrContextHandle))),

Method("s_sndevtResolveSoundAlias", 1, 
In(NdrWString), 
In(NdrUniquePTR(NdrWString)), 
In(NdrLong), 
Out(NdrLong), 
In(Out(NdrUniquePTR(NdrWString)))),

Method("s_pbmRegisterPlaybackManagerNotifications", 1, 
In(NdrShort), 
In(NdrShort)),

Method("s_pbmUnregisterPlaybackManagerNotifications", 1, 
In(NdrShort), 
In(NdrShort)),

Method("s_pbmSetSmtcSubscriptionState", 1, 
In(NdrShort), 
In(NdrLong)),

Method("s_pbmGetSoundLevel", 1, 
Out(NdrRef(NdrShort))),

Method("s_ccCreateHandsfreeHidFileFromAudioId", 1, 
In(NdrWString), 
Out(NdrLong)),

Method("s_pbmRegisterAppClosureNotification", 1, 
),

Method("s_pbmUnregisterAppClosureNotification", 1, 
),

Method("s_pbmPlayToStreamStateChanged", 1, 
In(NdrShort)),

Method("s_pbmIsPlaying", 1, 
Out(NdrLong)),

Method("s_pbmCastingAppStateChanged", 1, 
In(NdrShort)),

Method("s_pbmLaunchBackgroundTask", 1, 
In(NdrWString), 
In(NdrWString), 
Out(Struct_96_t)),

Method("s_pbmRegisterAsBackgroundTask", 1, 
In(Struct_96_t)),

Method("s_afxOpenAudioEffectsWatcher", 1, 
In(NdrWString), 
In(NdrShort), 
In(NdrLong), 
Out(Struct_96_t), 
Out(NdrHyper), 
Out(NdrContextHandle)),

Method("s_afxCloseAudioEffectsWatcher", 0, 
In(Out(NdrContextHandle))),

Method("s_midiOpenPort", 1, 
In(NdrWString), 
Out(NdrLong)),

Method("s_rtgGetDefaultAudioEndpoint", 1, 
In(NdrShort), 
In(NdrShort), 
Out(NdrRef(NdrWString)), 
Out(NdrLong)),

Method("s_apmRegisterProxyAudioProcess", 1, 
),

Method("s_apmSetDuckingGainForId", 1, 
In(NdrWString), 
In(NdrLong)),

Method("s_apmSetLayoutGainForId", 1, 
In(NdrLong), 
In(NdrLong)),

Method("s_apmSetVolumeGroupGainForId", 1, 
In(NdrWString), 
In(NdrLong)),
]) 

interface.is_registered = False

interface.endpoints = []
interface.endpoints.append("AudioClientRpc")
interface.endpoints.append("Audiosrv")
interface.endpoints.append("PlaybackManagerRpc")
interface.endpoints.append("AudioSrvDiagnosticsRpc")
interface.endpoints.append("SpatialSoundDataManagerRpc")
