def get_otp_challenge_key(channel: str, identifier: str) -> str:
    return f"otp:challenge:{channel}:{identifier}"

def get_otp_attempts_key(channel: str, identifier: str) -> str:
    return f"otp:attempts:{channel}:{identifier}"

def get_otp_cooldown_key(channel: str, identifier: str) -> str:
    return f"otp:cooldown:{channel}:{identifier}"
