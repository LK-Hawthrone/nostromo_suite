# Simple procedural Signal Bus
# Can be used to communicate status between modules

# Dictionary to hold signals
signals = {}

def emit_signal(signal_name, status, message=""):
    """
    Emit a signal to the bus.
    signal_name: str - unique identifier for the signal
    status: bool - True for success, False for failure
    message: str - optional message
    """
    signals[signal_name] = {"status": status, "message": message}
    print(f"[SIGNAL] {signal_name} -> status: {status}, message: '{message}'")

def get_signal(signal_name):
    """
    Retrieve a signal from the bus.
    Returns a dict with 'status' and 'message', or None if not found.
    """
    return signals.get(signal_name, None)

def clear_signal(signal_name):
    """
    Remove a signal from the bus.
    """
    if signal_name in signals:
        del signals[signal_name]