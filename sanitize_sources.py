import os

files = ['party.txt', 'workout.txt', 'sleep.txt', 'study.txt']

print("🧹 Cleaning source files...")
for filename in files:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            # Read all lines, strip whitespace, remove empties
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # Remove duplicates using set()
        unique_lines = sorted(list(set(lines)))
        
        # Write back to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(unique_lines))
            
        print(f"✅ {filename}: Now has {len(unique_lines)} unique songs.")
    else:
        print(f"⚠️ {filename} not found.")