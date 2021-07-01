import setuptools

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt", "r", encoding="utf-8") as req_file:
    requirements = req_file.readlines()

setuptools.setup(
    name="discord-lib",
    version="0.0.1",
    author="Swas.py",
    license="MIT",
    description="Create discord.py clients from XML, JSON, yaml etc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CodeWithSwastik/discord-lib",
    packages=["discordlib"],
    install_requires=requirements,
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
