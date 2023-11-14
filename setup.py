import os
from setuptools import setup, find_packages


# Get the README.md text
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
    readme = f.read()

# Parse vfxwindow/__init__.py for a version
with open(os.path.join(os.path.dirname(__file__), 'vfxwindow/__init__.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = eval(line.split('=')[1].strip())
            break
    else:
        raise RuntimeError('no version found')

# Get the pip requirements
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r') as f:
    requirements = [line.strip() for line in f]

setup(
    name = 'vfxwindow',
    packages = find_packages(),
    version = version,
    license='MIT',
    description = 'Qt window class for designing tools to be compatible between multiple VFX programs.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author = 'Peter Hunt',
    author_email='peter@huntfx.uk',
    url = 'https://github.com/huntfx/vfxwindow',
    download_url = 'https://github.com/huntfx/vfxwindow/archive/{}.tar.gz'.format(version),
    project_urls={
        'Documentation': 'https://github.com/huntfx/vfxwindow/wiki',
        'Source': 'https://github.com/huntfx/vfxwindow',
        'Issues': 'https://github.com/huntfx/vfxwindow/issues',
    },
    keywords = [
        'qt', 'pyside', 'pyside2', 'pyqt', 'pyqt4', 'pyqt5', 'gui', 'window',
        'maya', 'mayapy', 'nuke', 'nukescripts', 'houdini', 'unreal', 'engine', 'ue4',
        'blender', '3dsmax', '3ds', 'blackmagic', 'fusion', 'substance', 'designer',
        'vfx', 'visualfx', 'fx', 'cgi', '3d',
    ],
    package_data={'vfxwindow': ['palettes/*.json']},
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Software Development :: User Interfaces',
    ],
    include_package_data=True,
    python_requires=('>=2.7, !=3.0.*, !=3.1.*, !=3.2.*')
)
