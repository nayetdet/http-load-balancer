from enum import Enum

class DiscoveryTargetNetworkStrategy(str, Enum):
    PUBLISHED = "published"
    INTERNAL = "internal"
    BOTH = "both"
