from setuptools import setup, find_packages

NAME = "Henry Smith"
EMAIL = "smithh@anl.gov"
URL = "https://github.com/henryjsmith12/image-analysis"
VERSION = "0.1.3"
DESCRIPTION = "Python-based software for XRD data analysis."
LONG_DESCRIPTION = "Python-based software for XRD data analysis. Allows users to analyze raw XRD scan images and reciprocal space-converted datasets."

setup(
    name="image-analysis", 
    version=VERSION,
    author=NAME,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "matplotlib==3.5.3",
        "numpy==1.23.1",
        "PyQt5==5.15.7",
        "pyqtgraph==0.12.1",
        "rsMap3D==1.2.1",
        "spec2nexus==2021.1.3",
        "tifffile==2022.8.8",
        "xrayutilities==1.7.3"
    ],
    url=URL,
    keywords=["python", "pyqtgraph", "image-analysis", "xrd"]
)

