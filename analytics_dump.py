"""Quick analytics dump from Redis"""
from app import app, redis
import json
from datetime import datetime

if not redis:
    print("Redis not available")
    exit()

# Get all daily counts
keys = redis.keys('count_*')
data = []
for k in sorted(keys):
    val = redis.get(k)
    date = k.replace('count_', '')
    data.append((date, int(val) if val else 0))

print("=== DAILY TRAFFIC (all time) ===")
print("Date,Count")
for d, v in sorted(data):
    print(f"{d},{v}")

print()
print("=== MONTHLY SUMMARY ===")
monthly = {}
for d, v in data:
    month = d[:7]
    monthly[month] = monthly.get(month, 0) + v

for m in sorted(monthly):
    print(f"  {m}: {monthly[m]} total")

print()
print("=== RECENT 30 DAYS ===")
recent = sorted(data)[-30:]
for d, v in recent:
    bar = '#' * min(v, 50)
    print(f"  {d}: {v:4d} {bar}")

print()
# Popular languages
pop_lang = redis.get('popular_languages')
print("=== POPULAR LANGUAGES ===")
print(pop_lang)

pop_voices = redis.get('popular_voices')
print()
print("=== POPULAR VOICES ===")
print(pop_voices)
