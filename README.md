# debaker
Automatic CSS/HL2/GMod file detection

A tool/script I made with ChatGPT to detect baked files in a map. Instead of manually going through & cross-referencing a maps textures & models with CSS & HL2 .vpk's, you can use this tool to automatically detect any textures, models, or sounds that may be baked into the map. 

Usage:
1. Edit the .py script and change the paths to where the default lists are on your PC
2. Run the script
3. Choose a .zip

Make sure not to nest folders in the zip, i.e.:
* Correct: /de_dust2 textures.zip/materials
* Incorrect: /de_dust2 textures.zip/de_dust2 textures/materials
