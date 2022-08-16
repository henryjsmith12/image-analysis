# image-analysis
Python-based software for XRD data analysis. Allows users to analyze SPEC data, raw XRD scan images, and reciprocal space-converted datasets.

![image-analysis v0.1.0 GUI](https://github.com/henryjsmith12/image-analysis/blob/main/screenshots/readme_gui.png?raw=true)

## Getting Started

### Prerequisites

 - Python 3.8

### Installation

`imageanalysis` can be installed as either a Python package with `pip` or directory with `git clone`. If you are installing the project as a directory, you should also create a virtual environment.

#### PyPi

```
pip install image-analysis
```

#### Cloning the Repository

```
git clone https://github.com/henryjsmith12/image-analysis.git
```

### Creating a Virtual Environment

#### Conda Virtual Environment

1. After cloning the repository, create an Anaconda virtual environment using the `environment.yml` file. The environment name can be altered in that file. By default, the virtual environment is named `ia-env`.

   ```
   conda env create -f environment.yml
   ```

2. Activate the virtual environment.

   ```
   conda activate ia-env
   ```

3. Change into the repository directory.

    ```
    cd image-analysis
    ```

#### Python Virtual Environment

1. After cloning the repository, create the virtual environment.

    ```
    python -m venv ./image-analysis
    ```

    This will create a virtual environment in the the repository directory.

2. Activate the virtual environment.

   ```
   source ./image-analysis/bin/activate
   ```

3. Change into the repository directory.

    ```
    cd image-analysis
    ```

4. Install the dependencies using `requirements.txt`.

    ```
    pip install -r requirements.txt
    ```

### Execution

#### Python Module

```
from imageanalysis import app
app.run()
```

#### Directory

If not in the repository directory, change into the repository directory using `cd image-analysis`, and run

```
python imageanalysis.py
```

The GUI on startup should look like this:

![Empty image-analysis v0.1.0 GUI](https://github.com/henryjsmith12/image-analysis/blob/main/screenshots/readme_empty_gui.png?raw=true)

### Projects

`image-analysis` is built for displaying data from a Project, a preset directory structure that contains:
- A SPEC data source
- Accompanying raw images for each scan in SPEC source
- Configuration files for a both detector and instrument

See `image-analysis/sample_project` for a Project directory example.

## License
See [`LICENSE.txt`](https://github.com/henryjsmith12/image-analysis/blob/main/LICENSE) for more information.

## Author
[Henry Smith](https://www.linkedin.com/in/henry-smith-5956a0189/) - Co-op Student Technical at Argonne National Laboratory

## Support

* [Report bugs here](https://github.com/henryjsmith12/image-analysis/issues)
* Email author at [smithh@anl.gov](smithh@anl.gov)