from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class BurstRateThrottle(UserRateThrottle):
    """Short burst rate limit"""
    scope = 'burst'

class SustainedRateThrottle(UserRateThrottle):
    """Long-term rate limit"""
    scope = 'sustained'

class AnonBurstRateThrottle(AnonRateThrottle):
    """Anonymous user burst limit"""
    scope = 'anon_burst'