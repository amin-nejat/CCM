# Installation Instructions for the Functional Causal Flow [**Paper**](https://www.biorxiv.org/content/10.1101/2020.11.23.394916v2.abstract)

1. Download and install [**anaconda**](https://docs.anaconda.com/anaconda/install/index.html)
2. Create a **virtual environment** using anaconda and activate it

```
conda create -n fcf python=3.8
conda activate fcf
```

3. Install FCF package

```
git clone https://github.com/amin-nejat/FCF.git
cd FCF
pip install -r requirements.txt 
pip install -e .
```

4. Run demo file

```
python demo.py
```
