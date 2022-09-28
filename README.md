# AlphaFold2 pLDDT scores contextualized

TODO

## Usage

The commands described in the following subchapters are meant to be executed in a shell in the project root directory.

### 0. Environment

The project uses Python for scripts. The root directory contains a `requirements.txt` file that can be used to create an
appropriate environment. For instance, `python3 -m pip install -r requirement.txt` installs the dependencies in the
current Python environment.

For using the download script, the `wget` utility must be installed on the system.

### 1. Data download

The application relies on data from the [AlphaFold 2 database](https://alphafold.ebi.ac.uk/) ([[1]](#1) and [[2]](#2))
and precomputed disorder predictions from SETH [[3]](#3). The `download_human.sh` script downloads both datasets into
the `./data` subdirectory. (If not yet present, the directory is created for you.)

```shell
./download_human.sh
```

Before downloading, the script checks whether the data has changed on the server. To force a download, delete the
corresponding file in the `./data` subdirectory.

### 2. pLDDT score extraction

The pLDDT scores are stored [alongside the 3D residue position](https://alphafold.ebi.ac.uk/faq#faq-5) inside the PDB
files predicted by AlphaFold 2. The `extract_plddts.py` utility extracts and stores them in a `..._plddts.json` file
inside the `./data` subdirectory.

```shell
./extract_plddts.py
```

Note, that the program extracts the `.tar` file downloaded from the AlphaFold 2 database inside a temporary directory.
Since every `.pdb.gz` file from the archive is copied, this temporarily requires as much addition disk memory as the
initial download. This happens to ease the use of multiple processes using a Python `ProcessPoolExecutor`.

### 3. Run some visualization

The visualization not only loads the SETH predictions but also the extracted pLDDT scores. A small
[streamlit](https://streamlit.io/) app can be used to visualize both datasets.

```shell
python3 -m streamlit run load_data.py
```

## References

<a id="1">[1]</a>
Jumper, J., Evans, R., Pritzel, A. et al. Highly accurate protein structure prediction with AlphaFold. Nature 596, 583–589 (2021). https://doi.org/10.1038/s41586-021-03819-2

<a id="2">[2]</a>
Mihaly Varadi, Stephen Anyango, Mandar Deshpande, Sreenath Nair, Cindy Natassia, Galabina Yordanova, David Yuan, Oana Stroe, Gemma Wood, Agata Laydon, Augustin Žídek, Tim Green, Kathryn Tunyasuvunakool, Stig Petersen, John Jumper, Ellen Clancy, Richard Green, Ankur Vora, Mira Lutfi, Michael Figurnov, Andrew Cowie, Nicole Hobbs, Pushmeet Kohli, Gerard Kleywegt, Ewan Birney, Demis Hassabis, Sameer Velankar, AlphaFold Protein Structure Database: massively expanding the structural coverage of protein-sequence space with high-accuracy models, Nucleic Acids Research, Volume 50, Issue D1, 7 January 2022, Pages D439–D444, https://doi.org/10.1093/nar/gkab1061

<a id="3">[3]</a>
Ilzhoefer, D., Heinzinger, M. & Rost, B. 2022. SETH predicts nuances of residue disorder from protein embeddings, https://doi.org/10.1101/2022.06.23.497276 (Preprint)
