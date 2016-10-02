# -*- mode: python -*-
a = Analysis(['nba2k16qt.py'],
             pathex=['..\\gk_blender_lib\\modules\\', 'C:\\Python27-x64\\Lib\\site-packages',
                     'L:\\Users\\gregkwaste\\Documents\\Projects\\NBA2K16 Explorer'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

# Fixing the pyconfig.h warning
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

# Exclude VLC dlls
for d in a.binaries:
    if 'vlc' in d[0]:
        a.binaries.remove(d)
    elif 'libgcc_s_seh-1' in d[0]:
        a.binaries.remove(d)

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='NBA2K_Explorer.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True, version='version.txt', icon='resources\\tool_icon.ico')
