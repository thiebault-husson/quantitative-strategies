import pandas as pd
import numpy as np

def normalize_matrix(matrix):
    df = matrix.copy()
    row_sums = df.sum(axis=1)
    rows_to_normalize = row_sums > 1.0
    if not rows_to_normalize.any():
        return matrix
    normalized = df.copy()
    for idx in df.index[rows_to_normalize]:
        row_sum = row_sums[idx]
        normalized.loc[idx] = df.loc[idx] / row_sum
    return normalized
