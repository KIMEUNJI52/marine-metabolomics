# =====================================================================
# R 대사체분석 패키지 설치 스크립트
# 실행:  Rscript R/install_packages.R   (conda 환경 활성화 후)
# =====================================================================

# CRAN 미러 설정
options(repos = c(CRAN = "https://cloud.r-project.org"))

# --- Bioconductor 설치기 확인 ---
if (!requireNamespace("BiocManager", quietly = TRUE)) {
  install.packages("BiocManager")
}

# --- Bioconductor 대사체분석 핵심 패키지 ---
bioc_pkgs <- c(
  "xcms",        # LC-MS 피크 검출·정렬 (대사체 전처리 표준)
  "CAMERA",      # 어덕트/동위원소 그룹핑
  "MSnbase",     # 질량분석 데이터 구조
  "limma",       # 차등 분석
  "pcaMethods",  # 결측 대응 PCA
  "impute",      # 결측치 대치
  "ropls"        # PCA/PLS-DA/OPLS-DA (대사체 다변량 분석) - Bioconductor 패키지
)

# --- CRAN 통계/시각화 보조 패키지 ---
cran_pkgs <- c(
  "vegan",       # 생태·군집 통계 (환경 연관 분석에 유용)
  "factoextra",  # 다변량 시각화
  "ggpubr",      # 출판용 그림
  "pheatmap"     # 히트맵
)

cat(">>> Bioconductor 패키지 설치...\n")
BiocManager::install(bioc_pkgs, update = FALSE, ask = FALSE)

cat(">>> CRAN 패키지 설치...\n")
to_install <- cran_pkgs[!(cran_pkgs %in% rownames(installed.packages()))]
if (length(to_install)) install.packages(to_install)

cat(">>> 설치 완료. 로드 테스트:\n")
for (p in c(bioc_pkgs, cran_pkgs)) {
  ok <- suppressWarnings(requireNamespace(p, quietly = TRUE))
  cat(sprintf("  [%s] %s\n", ifelse(ok, "OK", "실패"), p))
}
