from sync_engine import normalize_arabic

def test_normalization():
    test_cases = [
        ("الْعَرَبِيَّةُ", "العربيه"),
        ("أهلاً بِكَ", "اهلا بك"),
        ("سورةُ الْبَقَرَةِ", "سوره البقره"),
        ("مُحَمَّدٌ", "محمد"),
        ("إلى", "الي"),
    ]
    
    for input_text, expected in test_cases:
        result = normalize_arabic(input_text)
        print(f"Input: {input_text} -> Result: {result} (Expected: {expected})")
        assert result == expected

if __name__ == "__main__":
    try:
        test_normalization()
        print("\nAll normalization tests passed!")
    except AssertionError as e:
        print("\nTest failed!")
