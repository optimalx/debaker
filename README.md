# optimizer
Automatic CSS/HL2/GMod & .sw.vtx/.xbox.vtx file detection & deletion

A Python tool/script I made with ChatGPT to detect baked files in a map. Instead of manually going through & cross-referencing a maps textures & models with CSS & HL2 .vpk's, you can use this tool to automatically detect any textures, models, or sounds that may be baked into the map (zip archive). The tool also detects .sw.vtx/.xbox.vtx files and deletes them as well, so you can use this on stuff that isn't maps.

Usage:
1. Edit the .py script and change the paths to where the default lists are on your PC
2. Run the script
3. Choose a .zip

Make sure the folders in the .zip you are selecting aren't nested, i.e.:
* Correct: /de_dust2 textures.zip/materials/
* Incorrect: /de_dust2 textures.zip/de_dust2 textures/materials/
