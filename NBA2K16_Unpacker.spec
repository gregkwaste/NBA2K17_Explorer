# -*- mode: python -*-
a = Analysis(['unpacker2k16.py'],
             pathex=['..\\gk_blender_lib\\modules\\', 'L:\\Users\\gregkwaste\\Documents\\Projects\\NBA2K16 Explorer'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='NBA2K16_Unpacker.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , icon='tool_icon.ico')
