# 클로드 점검 지시문 (확인 대기 → 공개)

대표님 지시(2026-11-03): 「25개중에 정보가 찾아지지 않거나 정보가 안보이는 경우나 보조 확인이 필요할 경우 클로드를 통해서 다시 점검해서 정보를 보충한다음에 캘린더로 넘겨줘야할 것 같아.」

점검 주기: 매주 월·수·금 08:30(대표님 확정 2026-11-03, 회사 맥북 예약 작업 「【월·수·금】정출연 캘린더 공고 점검」). 대표님이 「캘린더 점검해」라고 하면 그때도 한다.

캘린더는 `data/jcy_calendar.json`의 `items`만 띄운다. 자동 수집(`scripts/fetch.py`, 매일 06:23, 예비 07:47)은 새 공고를 `pending`에만 넣는다. 클로드가 아래 순서로 확인해 `items`로 옮긴다.

## 0. 자동 수집이 오늘 돌았는지 먼저 본다
- GitHub 예약 실행이 걸리지 않는 일이 있어(2026-11-04 두 번 확인), 회사 맥북이 매일 06:45에 오늘 수집 여부를 보고 안 됐으면 `gh workflow run`으로 수동 실행한다(launchd `kr.careerpeak.calendar-fetch`, 기록 `~/Library/Logs/careerpeak-calendar-fetch.log`). 맥이 잠자기였으면 깨어날 때 돈다.
- `gh run list --workflow update.yml --event schedule -L 3`에 오늘(한국 날짜) 성공한 실행이 있는지, `data/jcy_calendar.json`의 `updated_at`이 오늘인지 본다.
- 없으면 `gh workflow run update.yml`로 수동 실행하고 `gh run watch`로 끝까지 기다린 뒤 `git pull --rebase`하고 점검을 시작한다. 보고에 「예약 실행 빠짐, 수동 실행함」을 적는다.

## 1. pending (자동 수집, 확인 전)
1. 공고 원문을 연다. fairy 공고는 `https://{약칭}.fairy.im/api/company/announcement/{번호}`(본문과 첨부파일 주소), KARI는 `https://kari.applyin.co.kr/jobs/{번호}`.
2. 공고문(본문, PDF·HWP 첨부)에서 읽어 채운다.
   - `degrees`: 지원할 수 있는 학위(학사·석사·박사). 분야마다 다르면 모두 적고 `degree_note`에 한 줄 설명.
     - 학력 무관·학력 요건 없음이면 `degrees: []`(빈 목록)로 두고 `degree_note`에 「학력 무관」 등을 적는다. `null`은 확인 전, `[]`는 학력 무관으로 구분한다(위젯이 「학력 무관」을 띄우는 기준).
     - 분야 가운데 일부만 무관이면 학사·석사·박사를 모두 넣고 `degree_note`에 분야별로 적는다.
   - `job_types`: 연구·기술·행정 가운데 모집하는 직군.
   - `category`가 틀렸으면 고친다(정규직, 인턴·연수, 박사후·연수연구원, 비정규·기타).
   - `evidence`: 확인한 곳(예: 「공고문 PDF 2쪽 응시자격」).
   - 칼럼: 위젯은 `column_url` → `data/jcy_columns.json`의 그 기관 칼럼(인턴·연수 공고면 「인턴」 글, 그다음 같은 직군 글, 직군 표시 없는 글, 아무 글) → 직군 공통 칼럼 순으로 고른다. 칼럼은 공고의 성격(고용형태: 박사후·인턴·계약직 등, 직무: 연구·기술·행정·기획 등, 대상 학위)에 맞는 글을 고른다(대표님 확정 2026-11-05). 기관 이름이 붙은 글이라도 성격이 다르면(예: 박사후 공고에 그 기관 정규직 연구직 글) 성격이 맞는 공통 글이 우선이다. 위젯이 고를 글이 공고 성격과 맞지 않으면 더 맞는 글의 `column_url`(careerpeak.co.kr 글 주소)과 `column_title`을 넣는다. 새 칼럼이 발행되면 `build_column_map.py`(로컬 `홈페이지_캘린더/` 폴더)를 다시 돌려 `data/jcy_columns.json`을 올린다.
3. `checked_by: "claude"`, `checked_at`(한국 시각)을 넣고 `reasons`·`found_at`을 지운 뒤 `items`로 옮긴다.
4. 연구·기술·행정 이외 직종(조리원, 경비, 환경미화 등)만 뽑는 공고는 캘린더에 넣지 않는다(대표님 확정 2026-11-03). `pending`에서 빼서 `excluded`로 옮긴다(`id`, `org`, `org_short`, `title`, `end`, `url`, `reason`, `excluded_by: "claude"`, `excluded_at`). 자동 수집은 `excluded`에 있는 공고를 다시 `pending`에 넣지 않고, 마감일이 지나면 목록에서 지운다.
5. 원문으로도 확인되지 않으면 `pending`에 남기고 `check_note`에 이유를 적는다(예: 「첨부 HWP 열 수 없음」). 대표님 보고 목록에 올린다. `check_note`는 다음 자동 수집 뒤에도 남는다.

## 2. review_queue (누리집 게시판 새 글)
- 글을 열어 실제 채용 공고인지 본다. 채용 공고면 1번과 같은 항목을 만들어 `items`에 넣는다(`id`: `{약칭}-board-{접수 시작일}`, `source: "board"`). 채용 공고가 아니면 지운다.

## 3. errors (열리지 않은 출처)
- 그 기관 공고를 다른 길(NST 공동채용 게시판, 기관 누리집, 에고브라우저)로 확인한다. 빠진 공고가 있으면 2번처럼 넣는다.

## 3-1. 과기 기관 28곳 (`data/sci_calendar.json`, 2026-11-10부터)
- 대표님 지시(2026-11-09): 정출연 밖 과학기술 공공기관 28곳(`data/orgs_sci.json`)도 캘린더로 만든다. 위젯은 정출연만 / 과기 28곳만 / 둘 다 세 가지로 바꿔 본다.
- 자동 수집은 `scripts/fetch_sci.py`(ALIO 진행중 목록, applyin KTR·ADD, 누리집 게시판 14곳 새 글). 형식과 규칙은 jcy_calendar.json과 같다(items·pending·review_queue·errors·excluded, 공고마다 `group`).
- 점검도 1~3번과 같다. ALIO 공고는 상세(`job.alio.go.kr/recruitview.do?idx=`)와 첨부로 원문을 본다. 연구·기술·행정 밖 직무(의사·간호사·미화·시설관리, 인재풀 상시 등록 등)는 excluded로 옮긴다.
- 브라우저로만 열리는 곳(KOPRI·KBRI·NNFC·KATECH·KETEP·KICET 상세)은 수집되지 않는다. 화·목 과기공공 작업 기록(`회사맥북/기록/YYYY-MM-DD_과기공공채용접수현황.md`)에서 접수 중 공고를 찾아 원문을 확인하고 items에 직접 넣는다(`id`: `{약칭}-board-{접수 시작일}`, `source: "board"`). 이렇게 넣은 공고는 자동 수집이 마감일까지 남긴다.

## 4. 저장
- 바뀐 `data/jcy_calendar.json`을 저장소에 올린다. 자동 수집과 겹치지 않게 06:20~06:35, 07:45~08:00은 피한다(겹쳐서 push가 거절되면 `git pull --rebase` 뒤 다시 push).
- 올리는 방법(2026-11-03부터): 회사 맥북의 작업 사본 `~/careerpeak-calendar`에서 `git pull --rebase` → 파일 고침 → `git commit` → `git push`. 인증은 gh 로그인(HARI7211, 맥 키체인)을 git이 쓴다. 웹 업로드 화면은 쓰지 않는다. 올린 뒤 `?ref={커밋}`으로 받아 로컬 파일과 대조한다.
- 다음 자동 수집은 `items`에서 `checked_by`가 있는 항목의 확인 내용(학위·직군 등)은 그대로 두고 날짜·상태만 원문 기준으로 고친다. 원문 제목·날짜가 바뀌면 `changed`에 표시되므로 다음 점검 때 다시 본다.

## 지킬 것
- 공고 본문을 옮겨 적지 않는다. 확인하지 못한 값은 비운다. 추측해서 채우지 않는다.
- 발표일은 넣지 않는다.
