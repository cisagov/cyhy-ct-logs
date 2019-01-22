from setuptools import setup, find_packages

setup(
    name='admiral',
    version='0.0.1',
    author='Mark Feldhousen',
    author_email='mark.feldhousen@trio.dhs.gov',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
          'admiral=admiral.celery:main',
        ],
    },
    license='LICENSE.txt',
    description='The Admiral',
    #long_description=open('README.md').read(),
    install_requires=[
        "celery >= 4.2.0",
        "redis == 2.10.6", # pinned due to https://github.com/celery/celery/issues/5175
        "docopt >= 0.6.2",
        "PyYAML >= 3.12",
        "schedule >= 0.4.2",
        "requests >= 2.21.0",
        "xmljson >= 0.2.0",
        "cryptography >= 2.4.2",
        "dnspython",
        "pytest >= 4.1.1",  #TODO get pip install -e to pickup tests_require
        "mock"
    ],
    # tests_require=[
    # 'pytest',
    # 'mock'
    # ]
)
