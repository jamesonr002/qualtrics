# ===============================================
# Program: 00_test_analysis.py
# Author: Jameson Roth
# Date: 2026 09 30
# Description: Complete preliminary analysis on test data
# ===============================================

import polars as pl
from qualtrics.config import DATA_DIR
from zipfile import ZipFile

zipped = f"{DATA_DIR}/raw/PLAY+TEST_+Employee+Round+1+-+for+dissemination_September+29,+2026_05.52.zip"
sample = pl.read_csv(
    ZipFile(zipped).read(
        "PLAY TEST: Employee Round 1 - for dissemination_September 29, 2026_05.52.csv"
    )
)

"""
Get number of people who failed attention checks
"""

# Correct answers for attn checks
check1_c = "Down"
check2_c = "Circle"

checks = sample.select("CHECK1", "CHECK2").remove(
            # filter out people who didn't answer either one
            pl.col("CHECK1").is_null() & pl.col("CHECK2").is_null()
        )
check1 = checks["CHECK1"].value_counts()
checks_pop = check1.sum().select('count').item()
check1_c_count = check1.filter(pl.col("CHECK1") == check1_c).select('count').item()
check2 = checks["CHECK2"].value_counts()
check2_c_count = check2.filter(pl.col("CHECK2") == check2_c).select('count').item()

print("ATTENTION CHECK SHARE CORRECT:")
print(f"CHECK 1: {check1_c_count/checks_pop:.2f}")
print(f"CHECK 2: {check2_c_count/checks_pop:.2f}")

"""
Sudoku statistics
"""

sudoku = (
    sample.select(
        "FT_total_correct", "STE_total_correct", "STH_total_correct", "HARD", "EASY"
    )
    .with_columns(pl.all().cast(pl.Int64, strict=False))
    .drop_nulls()
)

pl.Config.set_tbl_rows(-1)
sudoku = sudoku.with_columns(
    (
        pl.col("STH_total_correct").sum()
        / pl.col("STH_total_correct").filter(pl.col("HARD") == 1).count()
    ).alias("STH_avg"),
    (
        pl.col("STE_total_correct").sum()
        / pl.col("STE_total_correct").filter(pl.col("EASY") == 1).count()
    ).alias("STE_avg"),
    (
        pl.col("STH_total_correct").filter(pl.col("HARD") == 1).std()
    ).alias("STH_std"),
)
print("FIRST TASK AVERAGE CORRECT:")
print(sudoku["FT_total_correct"].mean())
print("FIRST TASK STANDARD DEV:")
print(f"{sudoku["FT_total_correct"].std():.2f}")

easy_hard = sample.select("EASY", "HARD").with_columns(pl.all().cast(pl.Int64, strict=False))

print("EASY/HARD DISTRIBUTION:")
print("EASY:")
easy_pop = easy_hard.filter(pl.col.EASY == 1).select("EASY").sum().item()
print(easy_pop)
print("HARD:")
hard_pop = easy_hard.filter(pl.col.HARD == 1).select("HARD").sum().item()
print(hard_pop)


"""
Demographic and Separation RV Distribution
"""
demo_sep = sample.select("demo_rand", "sep_rand").with_columns(pl.all().cast(pl.Int64, strict=False))
print("DEMOGRAPHIC = 1 & SEPARATION = 1:")
print(demo_sep.filter((pl.col.demo_rand == 1) & (pl.col.sep_rand == 1)).count())

print("DEMOGRAPHIC = 1 & SEPARATION = 0:")
print(demo_sep.filter((pl.col.sep_rand == 0) & (pl.col.demo_rand == 1)).count())

print("DEMOGRAPHIC = 0 & SEPARATION = 1:")
print(demo_sep.filter((pl.col.sep_rand == 1) & (pl.col.demo_rand == 0)).count())

print("DEMOGRAPHIC = 0 & SEPARATION = 0:")
print(demo_sep.filter((pl.col.sep_rand == 0) & (pl.col.demo_rand == 0)).count())
