from PyInstaller.utils.hooks import collect_submodules
import subprocess

subprocess.run(["pyinstaller", "main.py", "--onefile", "--windowed", "--add-data", "config.ini:."]) 
# pyinstaller main.py --onefile --windowed --specpath "C:/Users/Aironas/Documents/GitHub/ImagerApp/build/spec" --distpath "C:/Users/Aironas/Documents/GitHub/ImagerApp/build/dist" --workpath "C:/Users/Aironas/Documents/GitHub/ImagerApp/build/build"