import os
from setuptools import setup, find_packages


# Get the README.md text
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as f:
    readme = f.read()

# Parse vfxwindow/__init__.py for a version
with open(os.path.join(os.path.dirname(__file__), 'vfxwindow/__init__.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = eval(line.split('=')[1].strip())
            break
    else:
        raise RuntimeError('no version found')

setup(
    name = 'vfxwindow',
    packages = find_packages(),
    version = version,
    license='MIT',
    description = 'Qt window class for designing tools to be compatible between multiple VFX programs.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author = 'Peter Hunt',
    author_email='peterh@blue-zoo.co.uk',
    url = 'https://github.com/Peter92/vfxwindow',
    download_url = 'https://github.com/Peter92/vfxwindow/archive/{}.tar.gz'.format(version),
    project_urls={
        'Documentation' : 'https://github.com/Peter92/vfxwindow/wiki',
        'Source'        : 'https://github.com/Peter92/vfxwindow',
        'Issues'        : 'https://github.com/Peter92/vfxwindow/issues',
    },
    keywords = [
        'vfx', 'cgi', 'qt', 'maya', 'nuke', 'houdini', 'gui',
        'animation', 'pipeline','mayapy', '3d', 'window', 'pymel',
        'nukescripts', 'pyside', 'pyqt',
    ],
    package_data={'vfxwindow': ['palettes/*.json']},
    install_requires=[],
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
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Software Development :: User Interfaces',
    ],
    include_package_data=True,
    python_requires=('>=2.7, !=3.0.*, !=3.1.*, !=3.2.*')
)
