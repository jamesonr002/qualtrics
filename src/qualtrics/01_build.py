# ===============================================
# Program: 01_build.py
# Author: Jameson Roth
# Date: 2026 10 29
# Description: Analysis of employee survey 1 data
# ===============================================

import polars as pl
from qualtrics.config import DATA_DIR

fn = pl.read_excel(DATA_DIR / "raw/FN_r1_1.xlsx")
fw = pl.read_excel(DATA_DIR / "raw/FW_r1_1.xlsx")
mn = pl.read_excel(DATA_DIR / "raw/MN_r1_1.xlsx")
mw = pl.read_excel(DATA_DIR / "raw/MW_r1_1.xlsx")


def clean(data):
    tmp = (
        data.select(
            "prolific_pid",
            "ft_total_correct",
            "ste_total_correct",
            "sth_total_correct",
            "easy",
            "hard",
            "demo_rand",
            "sep_rand",
            "check1",
            "check2",
            "finished",
            "ethnicitysimplified",
            "sex",
            "age",
            "totalapprovals",
            "highesteducationlevelcompleted"
        )
        .filter(pl.col.finished == 1, pl.col.check1 == 2, pl.col.check2 == 3)
        .with_columns(
            pl.col.ste_total_correct.cast(pl.Int64),
            pl.col.sth_total_correct.cast(pl.Int64),
            pl.col.ft_total_correct.cast(pl.Int64),
        )
        .rename({"highesteducationlevelcompleted":"educ",
                 "ethnicitysimplified":"ethnicity"})
    )
    return tmp


def get_mean_scores(task):
    if task == "first":
        return merged.select(pl.mean("ft_total_correct"))
    if task == "easy":
        return merged.filter(pl.col.easy == "1").select(pl.mean("ste_total_correct"))
    if task == "hard":
        return merged.filter(pl.col.hard == "1").select(pl.mean("sth_total_correct"))

# TODO: pull in r2 data and match all users between r1 and r2


merged = pl.concat([clean(fn), clean(fw), clean(mn), clean(mw)]).with_row_index("index")
merged.write_csv(DATA_DIR / "clean/data_build.csv")


print(get_mean_scores("easy"))
print(get_mean_scores("hard"))
print(get_mean_scores("first"))
