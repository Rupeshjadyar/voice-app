"""
=============================================================================
AUTOMATED INTEGRITY TEST: VOICE ARCHITECTURE RULES (ALL 104 LANGUAGES)
=============================================================================
This test ensures that:
1. Zero Robotic Distortion: female-1..5 and male-1..5 have 1.00x rate and 0 pitch shift.
2. Zero Collision: In ALL 104 languages, female-1..5 and male-1..5 resolve to 5 unique voices each.
3. Total unique tests: 104 languages x 10 slots = 1,040 voice resolution validations.
=============================================================================
"""

import sys
import io

# Safe stdout encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app import COMPLETE_VOICE_CATALOG, VOICE_TYPE_MODIFIERS, get_voice

def test_modifiers_integrity():
    print("\n[1/2] Testing Voice Modifiers (Zero Distortion Rule)...")
    core_voices = [f"female-{i}" for i in range(1, 6)] + [f"male-{i}" for i in range(1, 6)]
    errors = []
    for cv in core_voices:
        mod = VOICE_TYPE_MODIFIERS.get(cv, {})
        rate = mod.get('rate_mult')
        pitch = mod.get('pitch_add')
        if rate != 1.0:
            errors.append(f"VIOLATION: {cv} has rate_mult={rate} (Must be exactly 1.0)")
        if pitch != 0:
            errors.append(f"VIOLATION: {cv} has pitch_add={pitch} (Must be exactly 0)")
    
    if errors:
        for e in errors:
            print("  [FAIL]", e)
        return False
    print("  [PASS] All Top 10 voices have 0Hz pitch shift and 1.00x speed (Zero Distortion)!")
    return True

def test_all_104_languages_uniqueness():
    print("\n[2/2] Testing Voice Uniqueness across ALL 104 Languages (Zero Collision Rule)...")
    total_langs = len(COMPLETE_VOICE_CATALOG)
    failed_langs = []
    
    for code, info in COMPLETE_VOICE_CATALOG.items():
        name = info.get('name', code)
        females = [get_voice(code, f"female-{i}") for i in range(1, 6)]
        males = [get_voice(code, f"male-{i}") for i in range(1, 6)]
        
        f_unique = len(set(females))
        m_unique = len(set(males))
        
        if f_unique != 5 or m_unique != 5:
            failed_langs.append({
                'code': code,
                'name': name,
                'f_count': f_unique,
                'm_count': m_unique,
                'females': females,
                'males': males
            })
    
    if failed_langs:
        print(f"  [FAIL] {len(failed_langs)} / {total_langs} languages had collisions:")
        for fl in failed_langs:
            print(f"     - {fl['code']} ({fl['name']}): Females={fl['f_count']}/5, Males={fl['m_count']}/5")
        return False
    
    print(f"  [PASS] ALL {total_langs} LANGUAGES PASSED 100% WITH ZERO COLLISIONS!")
    print(f"  [PASS] Every single language has 5 unique female voices and 5 unique male voices.")
    return True

if __name__ == '__main__':
    print("=" * 70)
    print("VOICE ARCHITECTURE INTEGRITY TEST SUITE")
    print("=" * 70)
    
    mod_ok = test_modifiers_integrity()
    uni_ok = test_all_104_languages_uniqueness()
    
    print("=" * 70)
    if mod_ok and uni_ok:
        print("[SUCCESS] 100% PASS! ALL RULES ARE STRICTLY ENFORCED & PROTECTED.")
        print("=" * 70)
        sys.exit(0)
    else:
        print("[FAILED] INTEGRITY TEST FAILED. DO NOT PROCEED.")
        print("=" * 70)
        sys.exit(1)
