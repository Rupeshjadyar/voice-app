import asyncio
import sys
import os

# Add root folder to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import VOICE_MAPPING

from edge_tts import VoicesManager

async def main():
    manager = await VoicesManager.create()
    valid_voices = {v['ShortName'] for v in manager.voices}
    
    invalid = []
    # Ignore languages that are not supported by edge-tts (they naturally fallback to gTTS)
    unsupported_languages = {'pa-IN', 'or-IN'}
    
    for key, val in VOICE_MAPPING.items():
        if key[0] in unsupported_languages:
            continue
        if val not in valid_voices:
            invalid.append((key, val))
            
    if invalid:
        print("FOUND INVALID VOICE MAPPINGS:")
        for key, val in invalid:
            print(f"Key {key} -> {val} (not in edge-tts available list)")
    else:
        print("ALL VOICE MAPPINGS ARE VALID!")

if __name__ == '__main__':
    asyncio.run(main())
