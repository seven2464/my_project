# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Login.py','Main.py','abcJudgment.py','ai.py','app.py','camera.py','dataShow.py','deleteAll.py','global_store.py','imageDetect.py','imagePDF.py','pdf.py','Setting.py','sparkAPI.py','speak.py','VideoDetect.py','videoPDF.py'],
    pathex=['C:\Users\wsh\Desktop\DetectionSystem2'],
    binaries=[('C:\Users\wsh\Desktop\DetectionSystem2\file','file'),('C:\Users\wsh\Desktop\DetectionSystem2\image','image'),('C:\Users\wsh\Desktop\DetectionSystem2\model','model'),('C:\Users\wsh\Desktop\DetectionSystem2\mysqlProject','mysqlProject'),('C:\Users\wsh\Desktop\DetectionSystem2\photo','photo'),('C:\Users\wsh\Desktop\DetectionSystem2\pictures','pictures'),('C:\Users\wsh\Desktop\DetectionSystem2\templates','templates'),('C:\Users\wsh\Desktop\DetectionSystem2\unet','unet'),('C:\Users\wsh\Desktop\DetectionSystem2\utils','utils')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Login',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='fangfajing.ico,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Login',
)
