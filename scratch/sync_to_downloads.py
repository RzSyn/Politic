# -*- coding: utf-8 -*-
import shutil
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

downloads_dir = r"C:\Users\ASUA\Downloads"

files_to_copy = [
    "website_constitution.html",
    "easy_summary.html",
    "thaksin.jpg",
    "abhisit.jpg",
    "pita.jpg",
    "mano.png",
    "traitisa_portrait.png"
]

# Add all pm*.jpg files
pm_files = glob.glob("pm*.jpg")
files_to_copy.extend(pm_files)

# Add all logo_* files
logo_files = glob.glob("logo_*")
files_to_copy.extend(logo_files)

copied_count = 0
for f in files_to_copy:
    if os.path.exists(f):
        shutil.copy(f, os.path.join(downloads_dir, f))
        copied_count += 1

print(f"✅ Successfully synced {copied_count} files to Downloads folder!")
