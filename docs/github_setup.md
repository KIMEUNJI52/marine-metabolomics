# GitHub 연결 방법

로컬 저장소는 이미 초기화되어 첫 커밋까지 완료된 상태입니다.
이제 GitHub에 올리기만 하면 됩니다. 두 가지 방법 중 하나를 고르세요.

## 방법 A: GitHub 웹에서 저장소 만들고 연결 (가장 간단)

1. https://github.com/new 접속
2. **Repository name**: `marine-metabolomics` (원하는 이름)
3. **Private / Public** 선택 (연구 데이터라면 보통 Private 권장)
4. README/.gitignore 는 **추가하지 말 것** (이미 로컬에 있음)
5. `Create repository` 클릭
6. 생성 후 나오는 주소를 아래처럼 연결 (터미널에서):

```powershell
cd C:\Users\RYU\projects\marine-metabolomics
git remote add origin https://github.com/<사용자명>/marine-metabolomics.git
git push -u origin main
```

7. push 시 로그인 창이 뜨면 GitHub 계정으로 로그인
   (또는 Personal Access Token 사용)

## 방법 B: GitHub CLI 사용 (한 번에)

```powershell
# gh CLI 설치 (관리자 권한 팝업 승인 필요)
winget install --id GitHub.cli -e

# 새 터미널에서 로그인
gh auth login

# 저장소 생성 + 연결 + push 한 번에
cd C:\Users\RYU\projects\marine-metabolomics
gh repo create marine-metabolomics --private --source=. --remote=origin --push
```

## 인증 팁
- HTTPS 방식은 **Personal Access Token(PAT)** 이 비밀번호를 대체합니다.
  - https://github.com/settings/tokens 에서 `Generate new token (classic)`
  - 권한: `repo` 체크
  - 생성된 토큰을 push 시 비밀번호 자리에 입력
- 한 번 로그인하면 Windows 자격 증명 관리자에 저장되어 이후 자동 로그인됩니다.

## 이후 일상 워크플로
```powershell
git add .
git commit -m "작업 내용 설명"
git push
```
