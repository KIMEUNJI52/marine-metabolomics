"""
연안 자생식물 대사체 데이터 가공 유틸리티.

대사체 정량 테이블(샘플 x 대사체)과 환경/샘플 메타데이터를 불러와
전처리(결측 처리, 정규화, 로그변환)하는 기본 함수 모음.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# 프로젝트 루트 기준 데이터 경로
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_META = ROOT / "data" / "metadata"


def load_feature_table(path: str | Path) -> pd.DataFrame:
    """대사체 피처 테이블 로드 (행=샘플, 열=대사체/피처)."""
    path = Path(path)
    if path.suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, index_col=0)
    return pd.read_csv(path, index_col=0)


def load_metadata(path: str | Path) -> pd.DataFrame:
    """샘플 메타데이터 로드 (샘플ID, 채집지, 염분, 수온, 종 등)."""
    return pd.read_csv(path, index_col=0)


def filter_missing(df: pd.DataFrame, max_missing: float = 0.3) -> pd.DataFrame:
    """결측 비율이 임계값을 넘는 대사체(열) 제거."""
    keep = df.isna().mean(axis=0) <= max_missing
    return df.loc[:, keep]


def impute_min(df: pd.DataFrame) -> pd.DataFrame:
    """대사체별 관측 최소값의 1/5로 결측 대치 (LOD 근사, 대사체 관행)."""
    filled = df.copy()
    for col in filled.columns:
        col_min = filled[col].min(skipna=True)
        filled[col] = filled[col].fillna(col_min / 5.0)
    return filled


def log_transform(df: pd.DataFrame) -> pd.DataFrame:
    """log2(x+1) 변환으로 분포 안정화."""
    return np.log2(df + 1.0)


def pareto_scale(df: pd.DataFrame) -> pd.DataFrame:
    """Pareto 스케일링 (평균 제거 후 표준편차 제곱근으로 나눔) - 대사체 표준 전처리."""
    centered = df - df.mean(axis=0)
    return centered / np.sqrt(df.std(axis=0))


def preprocess(df: pd.DataFrame, max_missing: float = 0.3) -> pd.DataFrame:
    """표준 전처리 파이프라인: 결측필터 → 대치 → 로그 → Pareto 스케일."""
    out = filter_missing(df, max_missing)
    out = impute_min(out)
    out = log_transform(out)
    out = pareto_scale(out)
    return out


if __name__ == "__main__":
    print(f"프로젝트 루트: {ROOT}")
    print(f"원본 데이터 경로: {DATA_RAW}")
    print("data_processing 모듈 로드 성공.")
