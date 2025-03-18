import pathlib
import json
import os, shutil

if os.name != "posix":
    print("Not running on linux! Likely not a raspberry PI!")
    if str(input("Are you sure you want to continue? (y/n) ")).upper() != "Y":
        quit()

path = pathlib.Path(__file__).parent.resolve()

with open(path / 'safeFromClear.json', "r") as f:
    rawData = json.load(f)

safeFiles = rawData["files"]

filesToRemove = []
foldersToRemove = []

for f in path.iterdir():
    if f.name not in safeFiles:
        if f.is_dir():
            foldersToRemove.append(f)
        else:
            filesToRemove.append(f)
if len(filesToRemove) > 0 or len(foldersToRemove) > 0:
    input(f'Found {len(filesToRemove)} files and {len(foldersToRemove)} folders\nFolders: {foldersToRemove}\nFiles: {filesToRemove}\nPress enter to remove the specified files and folders, press CTRL+C to abort.')
else:
    print("Found nothing.")

if len(filesToRemove) > 0:
    for f in filesToRemove:
        os.remove(path / f)
    print(f'Files removed!')

if len(foldersToRemove) > 0:
    for f in foldersToRemove:
        shutil.rmtree(path / f)
    print(f'Folders removed!')