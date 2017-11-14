import random
import windows
import windows.rpc
import windows.generated_def as gdef
import windows.rpc.ndr
from time import sleep, strftime
from os import fsync, listdir
from ndr import *

# Logging
def log(s, no_new_line = False, debug = False):
    """Save fuzzer logs"""
    from config import LOGFILE, FUZZ_LOG_MAX_SIZE_MB, DEBUG_STDOUT
    if LOGFILE and not debug:
        if not no_new_line:
            LOGFILE.write(strftime("[%d/%m %H:%M:%S] "))
        LOGFILE.write(s)
        if not no_new_line:
            LOGFILE.write('\n')
        # Check max logfile size and rotate
        position = LOGFILE.tell()
        if position >= (FUZZ_LOG_MAX_SIZE_MB * 1000 * 1000):
            LOGFILE.seek(0)
        # Sync to disk (useful in case of kernel crash)
        LOGFILE.flush()
        fsync(LOGFILE.fileno())
    if DEBUG_STDOUT:
        if no_new_line:
            print s,
        else:
            print s

# RPC classes

class Interface(object):
    def __init__(self, uuid, version, methods):
        """RPC Interface"""
        self.uuid = uuid
        self.version = version
        self.methods = methods
        self.update_methods_ids()
        self.contexts = set([])
        self.client = None
        self.iid = None
        
    def update_methods_ids(self):
        for i in xrange(len(self.methods)):
            self.methods[i].id = i
            
    def connect(self):
        """Connect to the interface using either epmapper RPC service or fixed ALPC endpoint name"""
        log("Try to connect to {} - {}".format(self.uuid, self.version), debug=True)
        if not hasattr(self, "is_registered") or self.is_registered:
            # Try epmapper to open ALPC endpoint and connect to it
            for known_sid in gdef.WELL_KNOWN_SID_TYPE.values:
                try:
                    self.client = windows.rpc.find_alpc_endpoint_and_connect(self.uuid, version=self.version, sid=known_sid)
                    self.iid = self.client.bind(self.uuid, version=self.version)
                    if self.iid:
                        break
                except Exception as e:
                    pass
            if not self.iid:
                log("Could not find a valid endpoint for target <{0}> version <{1}> with epmapper".format(self.uuid, self.version))
        if hasattr(self, "endpoints"):
            # Try ncalrpc endpoints
            for endpoint in self.endpoints:
                try:
                    self.client = windows.rpc.RPCClient("\\RPC Control\\" + endpoint)
                    self.iid = self.client.bind(self.uuid, version=self.version)
                    if self.iid:
                        break
                except:
                    pass
            if not self.iid:
                log("Could not connect to a valid endpoint for target <{0}> version <{1}>".format(self.uuid, self.version))
        # Fail ...
        if not self.iid:
            raise ValueError("Impossible to connect to {}".format(self.uuid))

    def disconnect(self):
        if hasattr(self, "client") and self.client:
            del self.client
    
    def call(self, method, argument):
        """Perform the RPC call"""
        if not self.client:
            raise(Exception("Not connected!"))
        if isinstance(method, str):
            method = self.find_method_by_name(method)
        if isinstance(method, Method):
            method = method.id
        return self._call(self.client, self.iid, method, argument)

    def _call(self, client, iid, method, arguments):
         return client.call(iid, method, arguments)

    def find_method_by_name(self, s):
        for i in xrange(len(self.methods)):
            if s.lower() == self.methods[i].name.lower():
                return i
        return None
         
    def fuzz(self, iterations):
        """Connect and fuzz the interface (iterations times)"""
        # Try to connect to an interface
        try:
            self.connect()
        except:
            return
        
        for _ in xrange(iterations):
            # Send data to a random method
            method_number = random.randint(0, len(self.methods) - 1)
            method = self.methods[method_number]
            if method.name in BLACKLIST_METHODS:
                continue
            
            log("Fuzzing : {} - {} ({})".format(self.uuid, method.name, method.id))
            try:
                forged_arguments = method.forge_call(self.contexts)
                
                if len(forged_arguments) > 0x1000:
                    log("Generated arguments too long {}".format(len(forged_arguments)))
                    continue
                
                log("Arguments")
                log(forged_arguments.encode('string-escape'))
                
                res = self.call(method, forged_arguments)
                
                # Extract any context_handle returned
                self.contexts |= set(method.extract_output(windows.rpc.ndr.NdrStream(res)))
                
            except Exception as e:
                # In case of a service crash:
                #   - WinDBG as postmortem debugger => Fuzzer hangs until the service is killed
                #   - No postmortem debugger => Service is restarted and message is lost
                if 'STATUS_MESSAGE_LOST' in str(e):
                    raw_input('[!] Stopped: CRASH in {} {}'.format(self.uuid, method.name))
                    exit(0)
                else:
                    log("Exception during the call - " + str(e)[:30])
                    log("Debug exception during RPC call : " + str(e), debug=True)
                
            
        
class Method(object):
    def __init__(self, name, n_first_arg, *args):
        """RPC Method"""
        self.name = name
        self.id = None
        self.arguments = args
        self.first_arg_idx = n_first_arg
    
    def _register_callback(self, opcode, *args):
        # SizeIs callback   : target, value
        # SwitchIs callback : target, value
        self.context['callbacks'].append((opcode, args))
    
    def apply_callbacks(self, args, alignments_infos = None):
        """After NDR generation update the value of SizeIs and SwitchIs arguments"""
        # Required to perform valid RPC calls
        for callback in self.context['callbacks']:
            opcode = callback[0]
            if not isinstance(opcode, SizeIs) and not isinstance(opcode, SwitchIs):
                raise(NotImplementedError('Unknown callback {}'.format(opcode)))
            
            target, value = callback[1]
            real_value = opcode.handle_modifier(value)
            
            if isinstance(opcode, SizeIs):
                log("Updating SizeIs argument {} => {}".format(target, value), debug=True)
            elif isinstance(opcode, SwitchIs):
                log("Updating SwitchIs argument {} => {}".format(target, value), debug=True)

            _, args[target] = self._forge_argument(self.context['members'][target], real_value, real_value)
            
            # Handle alignment
            if alignments_infos and alignments_infos[target]:
                args[target] = alignments_infos[target] + args[target]
            
        return args
    
    def _forge_struct(self, argument):
        """Handle structure: forge members and handle complex opcodes and alignment"""
        # Save context
        old_context = self.context
        self.context = {'callbacks': [], 'members': argument.MEMBERS, 'ignored_members': 0, 'current_size': old_context['current_size']}
        
        forged_params = []
        alignment_infos = []
        for member in argument.MEMBERS:
            current_size = self.context['current_size']
            # Dirty: Mark context as aligned for subs structs
            if self.context['current_size'] % 4 != 0:
                self.context['current_size'] = ((self.context['current_size'] / 4) + 1) * 4
            
            size, packed = self._forge_argument(member)
            
            packed_size = len(packed)
            padding = ''
            # Align structures members
            if current_size % min(packed_size, 4) != 0:
                padding = 'P' * (min(packed_size, 4) - (current_size % min(packed_size, 4)))
            
            alignment_infos.append(padding)
            forged_params.append(padding + packed)
            self.context['current_size'] = current_size + len(padding + packed)

        forged_params = self.apply_callbacks(forged_params, alignment_infos)
        
        # Restore context
        self.context = old_context
        return argument.pack(forged_params)
    
    def _forge_union(self, union, range_min, range_max):
       """Handle unions: Select a attribute and forge it"""
       # No need to swap context
       case_n, member = union.generate()
       size, subpack = self._forge_argument(member, range_min, range_max)
       packed = union.pack(case_n, subpack)
       return case_n, size, packed
    
    def _forge_argument(self, argument, range_min = RANGE_MIN_VALUE, range_max = RANGE_MAX_VALUE):
        """Base function to generate a NDR type"""
        if isinstance(argument, In) or isinstance(argument, Out):
            return self._forge_argument(argument.param, range_min, range_max)

        if isinstance(argument, NdrPtr):
            # Represent the pointer after subcls packed
            size, packed = self._forge_argument(argument.subcls, range_min, range_max)
            return size, argument.pack(packed)
        
        if isinstance(argument, SizeIs):
            # Verify if size argument has a Range
            target = argument.target - self.context['ignored_members']
            range_min, range_max = extract_range(self.context['members'][target])
            size, packed = self._forge_argument(argument.param, range_min, range_max)
            # Add callback to update the size
            self._register_callback(argument, target, size)
            return size, packed

        if isinstance(argument, SwitchIs):
            # Ignore target range
            target = argument.target - self.context['ignored_members']
            case_n, size, packed = self._forge_union(argument.param, range_min, range_max)
            # Add callback to update the target
            self._register_callback(argument, target, case_n)
            return size, packed
        
        if isinstance(argument, Range):
            return self._forge_argument(argument.param, max(argument.min, range_min), min(argument.max, range_max))
            
        # Structure
        if is_ndr_struct(argument):
            return 0, self._forge_struct(argument)
        
        # Generate it
        current_size, packed = argument.generate_and_pack(self.ctxs, range_min, range_max)
        
        # Alignment issue on Hyper
        if argument is NdrHyper:
            curr_size = self.context['current_size']
            if curr_size % 8 != 0: # if not aligned: add 4 bytes before
                current_size += 4
                packed = 'P' * 4 + packed
        
        return current_size, packed
        
    def forge_call(self, ctx):
        """Generate a valid random NDR stream"""
        self.ctxs = ctx
        self.context = {'callbacks': [], 'members': list(self.arguments), 'ignored_members': self.first_arg_idx, 'current_size': 0}
        
        # Forge argument one by one
        forged_params = []
        for argument in self.arguments:
            if isinstance(argument, Out):
                self.context['members'].remove(argument)
                self.context['ignored_members'] += 1
            if isinstance(argument, In):
                _, packed = self._forge_argument(argument.param)
                forged_params.append(packed)
                # Update total_size for alignment issues
                self.context['current_size'] = len(''.join(map(ndr_pad, forged_params)))
        
        # Apply the callbacks to handle SizeIs / SwitchIs opcodes
        forged_params = self.apply_callbacks(forged_params)
        
        return ndr_pad(''.join(map(ndr_pad, forged_params)))
        
    def extract_output(self, result):
        """Extract context_handle from the result NDR stream"""
        ctxs = []
        for arg in self.arguments:
            if isinstance(arg, In):
                arg = arg.param
            if isinstance(arg, Out):
                log("Unpacking argument type {}".format(arg.param), debug=True)
                try:
                    unpacked = arg.param.unpack(result)
                    if arg.param is NdrContextHandle:
                        ctxs.append(unpacked)
                except Exception as e:
                    log("Exception during output extraction: {}".format(str(e)), debug=True)
                    break
        if ctxs:
            log("Extracted contexts handle returned : {}".format(ctxs))
        return ctxs

class Fuzzer(object):
    def __init__(self):
        """Wrapper to fuzz multiples interfaces"""
        self.interfaces = []
    
    def __add__(self, interface):
        self.interfaces.append(interface)
        return self
    
    def try_connect_all_interfaces(self):
        """Helper to check the availability of interfaces"""
        count = 0
        for interface in self.interfaces:
            try:
                print "[?] Try to connect to", interface.uuid
                interface.connect()
                print "[+] Connected to", interface.uuid
                count += 1
            except Exception as e:
                print "[-] FAIL to connect : " + str(e)

        print "[!] Successfully connected to {} / {}".format(count, len(self.interfaces))
    
    def fuzz_one_random_interface(self, iterations):
        """Select and fuzz one random interface (iterations RPC calls)"""
        if not self.interfaces:
            return
        interface = random.choice(self.interfaces)
        try:
            interface.fuzz(iterations)
        except Exception as e:
            log("fuzz_one_random_interface exception : " + str(e))
        finally:
            interface.disconnect()
        
    def fuzz(self, interfaces, iterations):
        """Fuzz iterations times for a number interfaces of random interface"""
        while interfaces > 0:
            self.fuzz_one_random_interface(iterations)
            interfaces -= 1

def get_interface(uiid):
    """Helper to import a interface"""
    interface = __import__("interfaces.{}".format(uiid))
    return getattr(interface, uiid).interface

BLACKLIST_METHODS = [
                # Infinite wait
                "FwSubscribeForNewRulesNotification",
                "RpcWaitAsyncNotification",
                "RpcWaitAsyncNotificationEx",
                "EvtRpcRemoteSubscriptionWaitAsync",
                "EvtRpcRemoteSubscriptionNextAsync",
                "KapiReceiveKaUpdateRequest",
                "GetNotificationRpc",
                "InitializeSyncHandle",
                "RemoveSyncHandle",
                "RpcClosePowerHandle",
                "BdeSvcApipCheckADSchema", # very slow
                "Reset",
                "RpcWaitForSessionState",
                
                # Annoying process execution
                "RAiProcessRunOnce",
                "RAiLogonWithSmartCardCreds",
                "RpcPopSecurityDialog",
                
                # Kill process
                "AudioDGShutdownADG",
]


BLACKLIST_INTERFACES = [
                "2eb08e3e-639f-4fba-97b1-14f878961076",
]

if __name__ == "__main__":
    fuzz = Fuzzer()

    # Get all interfaces
    for item in listdir("interfaces"):
        try:
            if item.endswith(".py") and item != "__init__.py":
                item = item[:-3]
                if item in BLACKLIST_INTERFACES: # timeout after X minutes
                    continue
                fuzz += get_interface(item)
        except Exception as e:
            log("Can't import interface from {} : {}".format(item, str(e)), debug=True)
    
    log("Fuzzing start on {} interfaces !".format(len(fuzz.interfaces)))
    
    # Switch to low integrity
    current_token = windows.current_process.token
    current_token.set_integrity(int(gdef.SECURITY_MANDATORY_LOW_RID))
    
    # Fuzz n_ifs interfaces before stopping (n_calls_by_if RPC calls for each interface randomly picked)
    n_ifs = 100000
    n_calls_by_if = 50
    fuzz.fuzz(n_ifs, n_calls_by_if)