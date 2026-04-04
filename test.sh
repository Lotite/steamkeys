source ~/miniconda3/etc/profile.d/conda.sh
conda activate steamkeys_env
export PYTHONPATH=.
python src/tests/scraping_test.py
