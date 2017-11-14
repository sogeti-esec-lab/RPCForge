# NDR Generator
import uuid
import random
import struct
import windows
import windows.rpc.ndr as ndr
from generator import *

ndr_pad = ndr.dword_pad

class NdrType(object):
    @classmethod
    def generate_and_pack(cls, context_handles, range_min, range_max):
        size, obj = cls.generate(context_handles, range_min, range_max)
        return size, cls.pack(obj)

class NdrByte(ndr.NdrByte, NdrType):
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        v = generate_int(8, range_min, range_max)
        return 0, v

NdrSmall = NdrByte

class NdrShort(ndr.NdrShort, NdrType):
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        v = generate_int(16, range_min, range_max)
        return 0, v

NdrWChar = NdrShort

class NdrLong(ndr.NdrLong, NdrType):
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        v = generate_int(32, range_min, range_max)
        return 0, v
        
class NdrHyper(ndr.NdrHyper, NdrType):
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        v = generate_int(64, range_min, range_max)
        return 0, v
        
class NdrContextHandle(NdrType):
    @classmethod
    def pack(cls, data = 0):
        if data == 0:
            data = "00000000-0000-0000-0000-000000000000"
        return struct.pack("<I", 0) + str(bytearray(windows.com.IID.from_string(data)))

    @classmethod
    def unpack(self, stream):
        attributes, rawguid = stream.partial_unpack("<I16s")
        return str(uuid.UUID(bytes_le=rawguid))
        
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        v = random.choice(list(ctx | set([0])))
        return 0, v

class NdrCString(NdrType):
    @classmethod
    def pack(cls, data):
        if data is None:
            return None
        l = len(data)
        result = struct.pack("<3I", l, 0, l)
        result += data
        return ndr_pad(result)

    @classmethod
    def unpack(self, stream):
        maxcount = NdrLong.unpack(stream)
        offset = NdrLong.unpack(stream)
        count = NdrLong.unpack(stream)
        s = stream.read(count)
        return s
        
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        s = generate_str(False, range_min, range_max)
        return len(s), s

class NdrWString(NdrType):
    @classmethod
    def pack(cls, data):
        if data is None:
            return None
        l = (len(data) / 2)
        result = struct.pack("<3I", l, 0, l)
        result += data
        return ndr_pad(result)
    @classmethod
    def unpack(self, stream):
        maxcount = NdrLong.unpack(stream)
        offset = NdrLong.unpack(stream)
        count = NdrLong.unpack(stream)
        s = stream.read(count * 2)
        return s.decode("utf-16-le")
        
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        s = generate_str(True, range_min, range_max)
        return len(s) // 2, s

class NdrByteConformantArray(NdrType, ndr.NdrByteConformantArray):
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        v = map(ord, generate_str(False, range_min, range_max))
        return len(v), v

class NdrShortConformantArray(NdrType, ndr.NdrConformantArray):
    MEMBER_TYPE = NdrShort
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        v = map(ord, generate_str(False, range_min, range_max))
        return len(v), v
        
class NdrLongConformantArray(NdrType, ndr.NdrConformantArray):
    MEMBER_TYPE = NdrLong
    @classmethod
    def generate(cls, ctx, range_min, range_max):
        params = []
        for _ in xrange(random.randint(0, 0xff)):
            params.append(random.choice(long_generator.choices))
        return len(params), params

class NdrUnion():
    @classmethod
    def generate(cls):
        key = 'default'
        while key == 'default':
            key = random.choice(cls.MEMBERS.keys())
        return key, cls.MEMBERS[key]    
    @classmethod
    def pack(cls, tag, data):
        return cls.SWITCHTYPE.pack(tag) + data

class NdrStructure(ndr.NdrStructure):
    @classmethod
    def pack(cls, data):
        if not (len(data) == len(cls.MEMBERS)):
            raise ValueError("NdrStructure size mismatch")
        conformant_size = []
        res = []
        pointed = []
        for i, (member, memberdata) in enumerate(zip(cls.MEMBERS, data)):
            if hasattr(member, "pack_in_struct"):
                raise(NotImplementedError("Not handled pack_in_struct"))
            elif hasattr(member, "pack_conformant"):
                raise(NotImplementedError("Not handled pack_conformant"))
            else:
                packed_member = memberdata
                res.append(packed_member)
        return ndr_pad("".join(conformant_size)) + ndr_pad("".join(res)) + ndr_pad("".join(pointed))

class NdrPtr(object):
    def __init__(self, subcls):
        self.subcls = subcls
    def generate_and_pack(self, context_handles, range_min, range_max):
        size, v = self.subcls.generate(context_handles, range_min, range_max)
        packed = self.pack(self.subcls.pack(v))
        return size, packed
    def pack(self, data):
        return data
    def unpack(self, stream):
        ptr = ndr.NdrLong.unpack(stream)
        if not ptr:
            return None
        return self.subcls.unpack(stream)

class NdrRef(NdrPtr): {} # cant be null

class NdrUniquePTR(NdrPtr):
    def generate_and_pack(self, context_handles, range_min, range_max):
        size, v = self.subcls.generate(context_handles, range_min, range_max)
        if random.randint(1, 20) == 1: # 5% null ptr
            return 0, ndr.pack_dword(0)
        packed = self.pack(self.subcls.pack(v))
        return size, packed
    def pack(self, data):
        return ndr.pack_dword(random.randint(0, 0xffffffff)) + data

class UserMarshall(object):
    def __init__(self, subcls):
        self.subcls = subcls
    def generate_and_pack(self, context_handles, range_min, range_max):
        raise NotImplementedError("UserMarshall({}).generate_and_pack".format(extract_raw_type(self.subcls).__name__))
    def pack(self, data):
        raise NotImplementedError("UserMarshall({}).pack".format(extract_raw_type(self.subcls).__name__))
    def unpack(self, data):
        raise NotImplementedError("UserMarshall({}).unpack".format(extract_raw_type(self.subcls).__name__))

def extract_range(some_type):
    """Extract the range attribute in sub-types information of some_type"""
    while True:
        try:
            if isinstance(some_type, Range):
                return some_type.min, some_type.max
            some_type = some_type.param
        except:
            return RANGE_MIN_VALUE, RANGE_MAX_VALUE

def extract_raw_type(some_type):
    """Extract the NDR type in sub-types information of some_type"""
    while True:
        try:
            some_type = some_type.param
        except:
            return some_type

def is_ndr_struct(some_type):
    """Helper to check for NdrStructure"""
    try:
        if NdrStructure in some_type.__bases__:
            return True
    except AttributeError:
        pass
    return False

# RPC Method complex types

class Opcode(object):
    def __init__(self, param, *ignored): 
        self.param = param

class In(Opcode): {}

class Out(Opcode): {}

class InOut(Opcode): {}

class ComplexOpcode(Opcode):
    def __init__(self, target, modifier = None):
        self.target = target
        self.modifier = modifier
    
    def handle_modifier(self, data):
        if self.modifier:
            if self.modifier == 'deref':
                return data
            if self.modifier == '+1':
                return data - 1
            elif self.modifier == '-1':
                return data + 1
            elif self.modifier == '*2':
                return data / 2
            elif self.modifier == '/2':
                return data * 2
        return data
    
    def __div__(self, param):
        self.param = param
        return self
    
    def unpack(self, data):
        return self.param.unpack(data)
        
class Range(ComplexOpcode):
    def __init__(self, min, max):
        self.min = min
        self.max = max

class SizeIs(ComplexOpcode):
    def __div__(self, param):
        self.param = param
        # Uni-dimensional Conformant Arrays
        if param is NdrByte:
            self.param = NdrByteConformantArray
        elif param is NdrWChar:
            self.param = NdrShortConformantArray
        elif param is NdrCString:
            self.param = NdrByteConformantArray
        elif param is NdrWString:
            self.param = NdrShortConformantArray
        return self

LengthIs = SizeIs # not the same : size_is is the size of allocation whereas length_is is the size of data

class SwitchIs(ComplexOpcode): {}
