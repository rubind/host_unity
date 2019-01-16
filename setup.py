from setuptools import setup

setup(
    name='unity-host',
    version='dev',
    description='Testing Unity models that account for host galaxy effects',
    author='Benjamin Rose, David Rubin',
    aurhor_email='brose@stsci.edu, drubin@stsci.edu',
    url='',
    license='MIT',
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Operating System :: MacOS :: MacOS X',
          # 'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python'
          ],
    # py_modules=['p2simga'],  # click says to use this
    install_requires=[
        'click',
        'pystan',
        'numpy',
        'scipy'
        # 'matplotlib',
        # 'corner'
    ],  # 3.7 docs look like this should be packages?
    entry_points='''
        [console_scripts]
        unity=cli:cli
        ''',
)
