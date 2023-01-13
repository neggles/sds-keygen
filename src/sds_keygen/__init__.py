try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown (no version information available)"
    version_tuple = (0, 0, "unknown", "noinfo")


OPTION_CODES = [
    "25M",
    "40M",
    "50M",
    "60M",
    "70M",
    "100M",
    "150M",
    "200M",
    "250M",
    "300M",
    "350M",
    "500M",
    "750M",
    "1000M",
    "MAX",
    "AWG",
    "WIFI",
    "MSO",
    "FLX",
    "CFD",
    "I2S",
    "1553",
    "PWA",
]
