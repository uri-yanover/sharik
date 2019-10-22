from setuptools import setup, find_packages

setup(
    name="sharik",
    version="0.1.1",
    packages=find_packages(),
    description='A shar(1)-like utility with a programmatic fine-tuned API',
    author='Uri Yanover',
    author_email='throwaway+sharik@yanover.name',
    url='https://github.com/uri-yanover/sharik',
    entry_points={
        'console_scripts': [
            'sharik = sharik.cli:cli_main'
        ]
    },
    install_requires=['click', 'dataclasses']
)