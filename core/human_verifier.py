def verify_human():
    """
    Simple human verification (mini reCAPTCHA).
    Returns True if user passes, False otherwise.
    """
    print("\n[Human Verification] Please answer the question correctly to continue.")
    print("Question: How do you spell 'Blue' backwards?")
    answer = input("Answer: ").strip().lower()

    if answer == "eulb":
        print("[Human Verification] Passed!")
        return True
    else:
        print("[Human Verification] Failed!")
        return False
