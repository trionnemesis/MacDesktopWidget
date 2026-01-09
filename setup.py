"""
py2app setup configuration for MacDesktopWidget.
"""
from setuptools import setup

APP = ['src/python/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/icon.icns',  # Optional: Add app icon
    'plist': {
        'CFBundleName': 'MacDesktopWidget',
        'CFBundleDisplayName': 'Mac Desktop Widget',
        'CFBundleGetInfoString': 'macOS System Monitor with AI',
        'CFBundleIdentifier': 'com.trionnemesis.macdesktopwidget',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024 trionnemesis. All rights reserved.',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
        'LSUIElement': False,  # Set to True to hide from Dock
    },
    'packages': [
        'PyQt6',
        'psutil',
        'aiohttp',
        'asyncio',
        'pydantic',
        'src.python.core',
        'src.python.monitoring',
        'src.python.ai',
        'src.python.ui',
    ],
    'includes': [
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
    ],
    'resources': [
        'src/python/ai/prompts/zh_tw_templates.py',
    ],
    'optimize': 2,
    'strip': True,
    'semi_standalone': False,
    'site_packages': True,
}

setup(
    name='MacDesktopWidget',
    version='1.0.0',
    description='macOS System Monitor with AI-powered suggestions',
    author='trionnemesis',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'PyQt6>=6.4.0',
        'psutil>=5.9.0',
        'aiohttp>=3.8.0',
        'pydantic>=2.0.0',
    ],
)
