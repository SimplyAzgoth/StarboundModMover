# Dynamic Starbound Mod Mover + Renamer
By SimplyAzgoth (https://steamcommunity.com/id/SimplyAzgoth/)

## Description

This script dynamically searches for mods in your starbound workshop folder and moves them to the starbound\mods folder while naming them after their workshop title.

It moves all types of mods but only renames some that have a specific structure for safety.

Renames any 'content.pak' or 'contents.pak' file to the mod title and nothing else.

Examples:

- 731220462\contents.pak -> starbound\mods\Enhanced Storage.pak
- "{exampleID}\I don't like to follow naming convention.pak" -> "starbound\mods\I don't like to follow naming convention.pak"
- 764887546\contents.pak  -> "starbound\mods\Stardust Core.pak"
- 764887546\post.pak -> starbound\mods\post.pak

## How to use

- Install 'requests' using pip:
 
>pip install requests

- Open the main.py file with a text editor and edit the configuration options. 

- Run using python in the terminal:

>python.exe main.py


## DISCLAIMER
I am not that good of a coder. Please make an issue on here if you see one, and I'll try my best