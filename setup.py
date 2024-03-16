from cx_Freeze import setup, Executable

setup(name="Logic Simulation System",
      version="1",
      description="Software used to create logic circuits",
      executables=[Executable(script="systemv1.py",
                              base="Win32GUI",
                              icon="Assets/icon.ico")])
