from setuptools import setup, find_packages

NAME = "Henry Smith"
EMAIL = "smithh@anl.gov"
URL = "https://github.com/henryjsmith12/image-analysis"
VERSION = "0.0.2"
DESCRIPTION = "Python-based software for XRD data analysis."
LONG_DESCRIPTION = "Python-based software for XRD data analysis. Allows users to analyze SPEC data, raw XRD scan images, and reciprocal space-converted datasets."

setup(
    name="image-analysis", 
    version=VERSION,
    author=NAME,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    url=URL,
    keywords=["python", "pyqtgraph", "image-analysis", "xrd"]
)