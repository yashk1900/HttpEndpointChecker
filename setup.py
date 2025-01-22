from setuptools import setup

setup(
    name='fetch-health-check',
    version='1.0',
    description='A tool to monitor the health of HTTP endpoints',
    author='Yash Kothekar',
    author_email='yashkothekar1900@gmail.com',
    py_modules=['fetchURL'],
    install_requires=[
        'pyyaml',
        'requests',
        'aiohttp'
    ],
    entry_points={
        'console_scripts': [
            'fetch-health-check=fetchURL:main',
        ],
    },
)
