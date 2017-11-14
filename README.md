# RPC Forge

RPC Forge is a local Python fuzzer of Windows RPC interfaces available over ALPC.

The fuzzer parses the interfaces definitions and automatically performs valid calls on the RPC methods.

This is more a PoC than a real fuzzer. Its aim was to be able to forge a valid serialized stream reaching
 RPC methods code without being rejected by the **Windows RPC Runtime** (because of bad arguments type leading to error: *RPC_X_BAD_STUB_DATA*).

Thus, it doesn't contain any instrumentation in the server side to improve code coverage.

RPC Forge was part of our work on Windows RPC and was introduced at PacSec 2017: [A view into ALPC-RPC][SLIDES].

# Internal working

1. Select one random interface
2. Connect and bind to it through epmapper RPC service or fixed ALPC endpoint name (see **Usage**)
3. Randomly choose one method
4. Generate valid call arguments according to the method parameters types based on [Sulley Generator][SULLEY]
5. Save the logs (call information) in a local file (depends on *config.py*)
6. Perform the call with marshaled ([NDR][NDR]) generated arguments
7. Extract any *context_handle* from the returned stream (to forge calls expecting a valid *context_handle*)
8. Loop (Step 1 or Step 3)

# Deps

[PythonForWindows][PYTHONFORWINDOWS] providing a Python implementation to play with ALPC and RPC.

# Usage

The custom [RPCView decompiler][RPCDECOMPILER] to generate Python definitions of interfaces won't be provided.

Five examples of Windows 10 interfaces are available in [interfaces directory][RPCFORGEIFS].

```python
# Describe the RPC interface and methods in Python
from rpc_forge import *

# Interface UUID 552d076a-cb29-4e44-8b6a-d15e59e2c0af VERSION 1.0 (DLL iphlpsvc.dll)
interface = Interface("552d076a-cb29-4e44-8b6a-d15e59e2c0af", (1,0), [
    # Method number 0 "IpTransitionProtocolApplyConfigChanges"
    #   * has an implicit binding handle (n_first_arg=1)
    #   * take one parameter: [in]char arg_1
    Method("IpTransitionProtocolApplyConfigChanges", 1, In(NdrByte)),
    # Method number 1 "IpTransitionProtocolApplyConfigChangesEx"
    #   * has an implicit binding handle (n_first_arg=1)
    #   * take three parameters: 
    #       [in]char arg_1, 
    #       [in][range(0,65535)] long arg_2,
    #       [in][size_is(arg_2)] byte *arg_3
    Method("IpTransitionProtocolApplyConfigChangesEx", 1, 
        In(NdrByte), 
        In(Range(0,65535) / NdrLong), 
        In(SizeIs(2) / NdrCString)
    ),
])
# Fuzzer will try to connect using epmapper service
interface.is_registered = True
# Fuzzer will also try the ALPC endpoint \RPC Control\TeredoDiagnostics
interface.endpoints = ["TeredoDiagnostics"]
```

# Thanks

[RPCView][RPCVIEW] for interface IDL decompilation

# Author

* Mastho

[RPCVIEW]: https://github.com/silverf0x/RpcView
[RPCDECOMPILER]: https://github.com/silverf0x/RpcView/tree/master/RpcDecompiler
[PYTHONFORWINDOWS]: https://github.com/hakril/PythonForWindows
[RPCFORGEIFS]: https://github.com/sogeti-esec-lab/RPCForge/tree/master/interfaces
[SLIDES]: https://hakril.net/slides/A_view_into_ALPC_RPC_pacsec_2017.pdf
[SULLEY]: https://github.com/OpenRCE/sulley
[NDR]: https://msdn.microsoft.com/fr-fr/library/windows/desktop/aa378635(v=vs.85).aspx