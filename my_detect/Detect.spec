# -*- mode: python -*-

block_cipher = None


a = Analysis(['Detect.py'],
             pathex=['D:\\Pythonfile\\my_detect'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Detect',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
