from inspect import cleandoc

from setuptools import setup


setup(
    name = 'Noms',
    packages = ['noms',],
    version = '0.0.0',
    description = 'Noms recipe amazement',
    author = 'Cory Dodt',
    author_email = 'corydodt@gmail.com',
    url = 'https://github.com/corydodt/Noms',
    keywords = [],
    classifiers = [
        "Programming Language :: Python :: 3",
    ],
    scripts = 'bin/whisk bin/noms'.split(),
    extras_require={
        'dev': [
            'pytest',
            'pytest-twisted',
            'pytest-coverage',
            'pytest-flakes',
            'tox',
        ]
    },
    install_requires=cleandoc('''
        boto3>=1.9.120
        codado>=0.6.1
        future>=0.17.1
        gitpython>=2.1.11
        itsdangerous>=1.1.0
        klein>=17.10.0
        microdata>=0.6.1
        mongoengine>=0.17.0
        mnemonicode>=1.4.4
        treq>=18.6.0
        twisted>=17.1.0
        watchdog
        ''').split()
)
