import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csvquery",
    version="1.1.3",
    author="Houston Youth Computer Science Group",
    author_email="houstoncsgroup@gmail.com",
    description="A versatile Python package that allows you to execute MongoDB-style queries on CSV files and interact with them like SQL tables.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hycsg/csvquery",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',
    ],
    python_requires='>=3.4',
)