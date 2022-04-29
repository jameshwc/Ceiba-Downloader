# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['src/gui_main.py'],
             pathex=[],
             binaries=[],
             datas=[('src/resources/custom.qss', 'resources'),
                    ('src/resources/GenSenRounded-M.ttc', 'resources'),
                    ('src/resources/ceiba.ico', 'resources'),
                    ('src/ceiba/i18n/*', 'resources/i18n')],
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

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='ceiba-downloader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='resources/ceiba.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ceiba-downloader')
app = BUNDLE(coll,
       name='ceiba-downloader.app',
       icon='resources/ceiba.ico',
       bundle_identifier=None)
