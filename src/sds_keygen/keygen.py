from enum import Enum, unique
from dataclasses import dataclass
from collections import namedtuple
from hashlib import md5

SECRET_KEY = "5zao9lyua01pp7hjzm3orcq90mds63z6zi5kv7vmv3ih981vlwn06txnjdtas3u2wa8msx61i12ueh14t7kqwsfskg032nhyuy1d9vv2wm925rd18kih9xhkyilobbgy"
NULL = "\x00"
KEY_PAD = NULL * 16


@unique
class ModelId(str, Enum):
    sds1000x_e = "SDS1000X-E"
    sds2000x_e = "SDS2000X-E"
    sds2000x_plus = "SDS2000X+"
    sds2000x_hd = "SDS2000X-HD"
    sds5000x = "SDS5000X"
    zodiac = "ZODIAC-"


OptCode = namedtuple("OptCode", ["code", "name"])


class Option:
    def __init__(*args, **kwargs):
        pass


class BandwidthOption(Option):
    group = "Bandwidth"

    def __init__(self, bw: int, note: str = ""):
        self.note = note
        if bw == -1:
            self.name = "No Bandwidth Limit"
            self.code = "MAX"
        else:
            self.name = f"{bw}MHz Bandwidth Limit"
            self.code = f"{bw}M"


class ProtocolOption(Option):
    group = "Decode"

    def __init__(self, name: str, code: str, note: str = ""):
        self.name = name
        self.code = code
        self.note = note


class FeatureOption(Option):
    group = "Feature"

    def __init__(self, name: str, code: str, note: str = ""):
        self.name = name
        self.code = code
        self.note = note


@dataclass
class Options:
    Bandwidth = [
        BandwidthOption(bw=25),
        BandwidthOption(bw=40),
        BandwidthOption(bw=50),
        BandwidthOption(bw=70),
        BandwidthOption(bw=100),
        BandwidthOption(bw=150),
        BandwidthOption(bw=200),
        BandwidthOption(bw=250),
        BandwidthOption(bw=300),
        BandwidthOption(bw=350),
        BandwidthOption(bw=500),
        BandwidthOption(bw=750),
        BandwidthOption(bw=1000),
        BandwidthOption(bw=-1, note="This option generally does not apply."),
    ]
    Protocol = [
        ProtocolOption("CAN-FD", "CFD"),
        ProtocolOption("16 Digital Channels", "16LA"),
        ProtocolOption("FlexRay", "FLX"),
        ProtocolOption("I2S", "I2S"),
        ProtocolOption("Manchester", "MANC"),
        ProtocolOption("SENT", "SENT"),
        ProtocolOption("MIL-STD-1553B", "1553"),
    ]
    Feature = [
        FeatureOption("Mixed Signal Mode", "MSO"),
        FeatureOption("Power Analysis", "PWA"),
        FeatureOption("Arbitrary Waveform Generator", "AWG"),
        FeatureOption("USB WiFi Support", "WIFI", "Not available on all models"),
    ]

    @property
    def All(self):
        return self.Bandwidth + self.Protocol + self.Feature


def map_byte(val: bytes) -> str:
    if val not in range(0x30, 0x39) and val not in range(0x61, 0x7A):
        val = val % 0x24
        val += 0x57 if val > 9 else 0x30
    if val == 0x30:
        return chr(0x32).upper()
    if val == 0x31:
        return chr(0x33).upper()
    if val == 0x6C:
        return chr(0x6D).upper()
    if val == 0x6F:
        return chr(0x70).upper()
    return chr(val).upper()


def generate_key(model_id: ModelId, device_id: str, opt_code: str) -> str:
    device_id = device_id.replace("-", "")
    hash_bytes = md5(
        "".join(
            [
                SECRET_KEY,
                (model_id.value + "\n").ljust(32, NULL),
                opt_code.ljust(5, NULL),
                (device_id + "\n").ljust(32, NULL),
                (device_id + "\n").ljust(32, NULL),
                KEY_PAD,
            ]
        ).encode("ascii")
    ).digest()

    return "".join([map_byte(b) for b in hash_bytes])
