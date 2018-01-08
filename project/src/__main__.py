import os
import sys

# Adds project root to system paths.
cwd = os.getcwd()
sys.path.extend([cwd])

# Makes src folder the working directory.
main_dir = os.path.join(cwd,'src')
os.chdir(main_dir)

# Imports and runs main
import src.main
src.main.main()
