from setuptools import setup, find_packages

setup(
    name="fossa",
    version="0.0.1",
    author="Brian Hartvigsen",
    author_email="brian.andrew@brianandjenny.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "beautifulsoup4",
        "cachecontrol[filecache]",
        "click",
        "python-dateutil",
        "requests",
        "stevedore",
        "toml",
    ],
    entry_points={
        'fossa.plugin.registrar': [
            'porkbun = fossa.plugin.registrar.porkbun:Porkbun',
            'internetbs = fossa.plugin.registrar.internetbs:Internetbs',
            'easyname = fossa.plugin.registrar.easyname:Easyname',
            'resellerclub = fossa.plugin.registrar.resellerclub:ResellerClub',
            'foundationapi = fossa.plugin.registrar.resellerclub:FoundationAPI',
            'gandi = fossa.plugin.registrar.gandi:Gandi',
            'namecheap = fossa.plugin.registrar.namecheap:Namecheap'
        ],
        'console_scripts': [
            'fossa = fossa.__main__:cli'
        ]
    },
    classifiers=[
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Natural Language :: English",
    ]
)
