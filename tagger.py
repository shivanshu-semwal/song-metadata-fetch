#!/bin/env python3

import json
import os
import subprocess
import requests
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='tagger',
        description='Fill the metadata of a song.',
        epilog='@author Shivanshu',
        argument_default=None,
        add_help=True)
    parser.add_argument('filename')
    parser.add_argument(
        '-s', action='store_true',
        default=False, dest='prompt')
    args = parser.parse_args()

    MUSIC_FILE = args.filename
    if not os.path.isfile(MUSIC_FILE):
        print("Invalid music file.")
        exit(0)
    CMD = ["songrec", "audio-file-to-recognized-song", MUSIC_FILE]
    SONGREC_DATA = subprocess.run(CMD, capture_output=True)
    if SONGREC_DATA.returncode != 0:
        print("Unable to connect to songrec, check if songrec works.")
        exit(0)

    SONGREC_OBJ = json.loads(SONGREC_DATA.stdout.decode('utf-8'))
    if len(SONGREC_OBJ['matches']) == 0:
        print("Unable to identify:: " + MUSIC_FILE)
        exit(-1)
    METADATA = {}
    if 'generes' in SONGREC_OBJ['track']:
        METADATA["genre"] = SONGREC_OBJ['track']['genres']['primary']

    # SONGREC_OBJ['track']['sections'][0]["metadata"]
    # 0: will contain song
    #   - "metadata" - metadata
    #   - "metapages" - albumcover
    # 1: will contain lyrics
    # 2: will contain video
    # 3: will contain related

    for data in SONGREC_OBJ['track']['sections'][0]["metadata"]:
        METADATA[data['title']] = data['text']

    if "images" in SONGREC_OBJ['track']:
        METADATA["albumart"] = SONGREC_OBJ['track']['images']['coverart']

    METADATA["title"] = SONGREC_OBJ['track']['title']
    METADATA['artist'] = SONGREC_OBJ['track']['subtitle']

    print("Match found:")
    print(json.dumps(METADATA, indent=4))

    if not args.prompt:
        option = input("Change metadata(y/n): ").lower()
        if option != 'y':
            exit(0)
    print("Changing metadata...")

    command = ["mid3v2"]
    if "artist" in METADATA:
        command.extend(["-a", METADATA["artist"]])
    if "Album" in METADATA:
        command.extend(["-A", METADATA["Album"]])
    if "title" in METADATA:
        command.extend(["-t", METADATA["title"]])
    if "albumart" in METADATA:
        response = requests.get(METADATA['albumart'])
        open('/tmp/art.jpg', "wb").write(response.content)
        command.extend(["-p", "/tmp/art.jpg"])
    if "genre" in METADATA:
        command.extend(["-g", METADATA["genre"]])
    if "Released" in METADATA:
        command.extend(["-y", METADATA["Released"]])

    command.append(MUSIC_FILE)
    subprocess.run(command)
