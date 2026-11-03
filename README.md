# careerpeak-calendar

커리어피크(careerpeak.co.kr) 정출연 채용 캘린더가 읽는 공고 자료를 매일 자동으로 고치는 저장소입니다. API 키, 로그인, 브라우저 없이 돕니다.

## 어떻게 도나
- GitHub Actions가 매일 07:00(한국 시간)에 `scripts/fetch.py`를 실행합니다(`.github/workflows/update.yml`). 컴퓨터가 꺼져 있어도 됩니다.
- 24곳은 기관 채용 시스템(fairy.im)의 공고 목록, 한국항공우주연구원은 applyin 공고 목록에서 제목·접수 기간·상태를 읽습니다. NST 공동채용 목록으로 빠진 것을 보탭니다.
- 기관 채용 시스템에 공고가 잘 안 올라오는 6곳(KRRI·KFRI·KIMS·KFE·NIGT·KIER)은 누리집 게시판의 새 글을 찾아 `review_queue`에 넣습니다(사람 확인 후 반영).
- 새 공고는 `pending`(확인 대기)에 들어가고, 클로드가 공고 원문으로 학위·직군을 확인해 `items`로 옮긴 것만 캘린더에 뜹니다(`CHECK.md`).
- 결과는 `data/jcy_calendar.json`에 저장되고 GitHub Pages로 공개됩니다. 캘린더 위젯은 이 파일의 `items`만 읽습니다.

## 파일
- `data/jcy_calendar.json`: 캘린더 자료 (`items` 공개, `review_queue` 확인 대기, `errors` 수집 오류)
- `data/orgs.json`: 대상 기관 25곳
- `data/seen_boards.json`: 게시판 새 글 판별용 기록
- `data/SCHEMA.md`: 항목 정의
