from setuptools import setup, find_packages

def get_requires():
    with open('requirements.txt') as f:
        return f.read().splitlines()
    


setup(
    name='gemini-cli', # Add a package name
    version='0.1.0', # Add a version
    packages=find_packages(where='.'), # Find packages in the current directory
    package_dir={'': '.'}, # Map the root package directory correctly
    install_requires=get_requires(),
    entry_points={
        'console_scripts': [
            # Use a proper reference to a fully qualified module:function
            'gemini-cli = gemini_cli.run:main',
        ],
    },
    author='Amit Maindola',
    description='A command-line interface for interacting with the Gemini API.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    # Add other setup arguments, if needed
)