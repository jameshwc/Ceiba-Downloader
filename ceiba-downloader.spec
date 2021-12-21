# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['gui_main.py'],
             pathex=[],
             binaries=[],
             datas=[('custom.qss', '.'),
                    ('GenSenRounded-M.ttc', '.'),
                    ('ceiba.ico', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

import sys
platform = sys.platform if sys.platform != 'darwin' else 'mac'
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ceiba-downloader-'+platform,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='ceiba.ico')
