import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="btr",
    version="0.0.6",
    author="Kainjazz",
    author_email="kainjazz@gmail.com",
    description="Reporter from Behave to TestRail",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kainjazz/BTR",
    keywords=['Behave', 'Testrail', 'Test', 'BDD'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
)