from cx_Freeze import setup, Executable

base = None

executables = [Executable("anaxcel.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {
        'packages': packages,
    },
}
setup(
    name="<Anaxcel>",
    options=options,
    version="<1.0>",
    description='<Data Analyser>',
    executables=executables
)
