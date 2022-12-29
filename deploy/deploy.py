from PyInstaller.__main__ import run

from reid_annotation_tool import main


def deploy():
    run([
        main.__file__,
        '--name',
        'reid_annotation_tool.app',
        '--onefile'
    ])
