# =====================================================================
# 01_preprocess.R - 대사체 데이터 전처리 + 다변량 탐색 (템플릿)
# 실행:  Rscript R/01_preprocess.R
# =====================================================================

suppressPackageStartupMessages({
  library(tidyverse)
})

# --- 경로 (프로젝트 루트 기준) ---
root <- normalizePath(file.path(dirname(sys.frame(1)$ofile %||% "."), ".."),
                      mustWork = FALSE)
if (is.na(root) || root == "") root <- getwd()

feature_path <- file.path("data", "raw", "feature_table.csv")   # 행=샘플, 열=대사체
meta_path    <- file.path("data", "metadata", "sample_metadata.csv")

# --- 데이터 로드 (파일이 준비되면 주석 해제) ---
# feat <- read_csv(feature_path)  |> column_to_rownames("sample_id")
# meta <- read_csv(meta_path)

# --- 전처리 함수 ---
filter_missing <- function(mat, max_missing = 0.3) {
  keep <- colMeans(is.na(mat)) <= max_missing
  mat[, keep, drop = FALSE]
}
impute_min <- function(mat) {
  apply(mat, 2, function(x) { x[is.na(x)] <- min(x, na.rm = TRUE) / 5; x })
}
pareto_scale <- function(mat) {
  scale(mat, center = TRUE, scale = sqrt(apply(mat, 2, sd, na.rm = TRUE)))
}

preprocess <- function(mat, max_missing = 0.3) {
  mat |>
    filter_missing(max_missing) |>
    impute_min() |>
    (\(m) log2(m + 1))() |>
    pareto_scale()
}

# --- 예시: PCA (ropls 사용, 설치 후) ---
# library(ropls)
# X <- preprocess(as.matrix(feat))
# pca <- opls(X)                          # PCA
# plsda <- opls(X, meta$site)             # 채집지별 PLS-DA

cat("01_preprocess.R 템플릿 로드 완료. 데이터 준비 후 주석을 해제하세요.\n")
