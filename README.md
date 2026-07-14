# 대한민국 연안 자생식물 대사체분석 (Marine Coastal Plant Metabolomics)

대한민국 연안 해양환경을 배경으로, 해양 인근 자생 나무·식물의 **성장 및 변화**를
**대사체분석(metabolomics)** 으로 규명하는 연구 프로젝트입니다.

## 연구 개요
- **대상**: 대한민국 연안(갯벌/사구/해안림 등) 자생 수목·식물
- **환경 변수**: 염분, 조위, 수온, 해양환경 지표 등
- **분석**: 대사체 프로파일링 → 환경 요인과 성장/변화의 연관성 분석

## 기술 스택
| 용도 | 도구 |
|------|------|
| 환경 관리 | conda (Miniforge) |
| 데이터 가공 | Python 3.12 (pandas, numpy, scipy) |
| 통계/대사체 | R 4.4 + Bioconductor (xcms, CAMERA 등) |
| 시각화 | matplotlib, seaborn, plotly, ggplot2 |
| 버전 관리 | Git + GitHub |

## 폴더 구조
```
marine-metabolomics/
├── data/
│   ├── raw/         # 원본 데이터 (git 제외)
│   ├── interim/     # 중간 가공 데이터
│   ├── processed/   # 분석용 최종 데이터
│   └── metadata/    # 샘플/환경 메타데이터
├── notebooks/       # Jupyter 탐색 분석
├── R/               # R 스크립트 (대사체 전처리·통계)
├── src/             # Python 재사용 모듈
├── results/
│   ├── figures/     # 그림
│   └── tables/      # 표
└── docs/            # 문서
```

## 환경 설정 (재현)
```powershell
# 1) conda 환경 생성
conda env create -f environment.yml
conda activate marine-metab

# 2) R 대사체분석 패키지 설치 (Bioconductor)
Rscript R/install_packages.R
```

## 워크플로
1. `data/raw/`에 원본 데이터 배치 (질량분석 결과, 환경 측정값 등)
2. `data/metadata/`에 샘플 메타데이터 정리
3. Python 또는 R로 전처리 → `data/processed/`
4. 대사체 통계분석 → `results/`
