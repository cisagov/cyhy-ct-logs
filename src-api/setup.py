from setuptools import setup, find_packages

setup(
    name='cyhy_api',
    version='0.0.1',
    author='Mark Feldhousen',
    author_email='mark.feldhousen@trio.dhs.gov',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
          'cyhy-api-server=cyhy_api.api:main',
        ],
    },
    license='LICENSE.txt',
    description='Cyber Hygiene API Server',
    #long_description=open('README.md').read(),
    install_requires=[
        "Flask >= 1.0.2",
        "Flask-REST-JSONAPI >= 0.22.0",
        "celery >= 4.2.0",
        "redis == 2.10.6", # pinned due to https://github.com/celery/celery/issues/5175
        "docopt >= 0.6.2",
        "PyYAML >= 3.12",
        "cryptography >= 2.4.2",
        "python-dateutil >= 2.7.5",
        "pytest >= 4.1.1",  #TODO get pip install -e to pickup tests_require
        "mock"
    ],
    # tests_require=[
    # 'pytest',
    # 'mock'
    # ]
)
