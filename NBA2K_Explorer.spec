# -*- mode: python -*-

block_cipher = None


a = Analysis(['nba2k17qt.py'],
             pathex=['..\\gk_blender_lib\\modules\\', 'C:\\Python27-x64\\Lib\\site-packages\\', 'J:\\Projects\\NBA2K17 Explorer'],
             binaries=[],
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='NBA2K_Explorer',
          debug=True,
          strip=False,
          upx=False,
          console=True , version='version.txt', icon='resources\\tool_icon.ico')
