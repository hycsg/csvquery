import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csv-query",
    version="0.1.0",
    author="Houston Youth Computer Science Group",
    author_email="houstoncsgroup@gmail.com",
    description="A python package that allows you to execute NoSQL-style queries on CSV files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Houston-Youth-Computer-Science-Group/csv-query",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)