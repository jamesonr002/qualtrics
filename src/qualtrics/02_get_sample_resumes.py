# ===============================================
# Program: 01_get_sample_resumes.py
# Author: Jameson Roth
# Date: 2026 10 22
# Description: Construct JSON sample resumes for loading into employer survey
# ===============================================

from qualtrics.config import DATA_DIR
import polars as pl

sample = pl.read_csv(DATA_DIR / "clean/data_build.csv")

sample = (
    sample.filter(pl.col.sep_rand == 0)
    .with_columns(
        pl.when(pl.col.easy == 1)
        .then(pl.col.ste_total_correct)
        .when(pl.col.hard == 1)
        .then(pl.col.sth_total_correct)
        .otherwise(None)
        .alias("r1_score")
    )
    .remove(pl.col.r1_score.is_null())
)

# TODO: add round 2 score

sample_50 = sample.sample(50).select(
    "totalapprovals", "ethnicity", "educ", "sex", "age", "r1_score"
).with_row_index()
print(sample_50)

sample_50_json = sample_50.write_json(DATA_DIR / "clean/sample_resumes.json")
