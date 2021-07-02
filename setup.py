import setuptools
import re 

version = ''
with open('discordlib/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt", "r", encoding="utf-8") as req_file:
    requirements = req_file.readlines()

extras_require = {
    'xml': ['xmltodict'],
    'yaml': ['PyYAML'],
}

setuptools.setup(
    name="discord-lib",
    version=version,
    author="Swas.py",
    license="MIT",
    description="Create discord.py clients from XML, JSON, yaml etc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CodeWithSwastik/discord-lib",
    packages=["discordlib"],
    install_requires=requirements,
    extras_require=extras_require,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
)
