# jcy_calendar.json 항목 정의

| 키 | 뜻 |
|---|---|
| id | 출처 약칭 + 공고 번호 (예: KIMM-22, NST-98, KARI-23508) |
| org / org_short | 기관 이름 / 약칭 (`orgs.json`과 같음) |
| title | 공고 제목(원문 그대로) |
| category | 제목으로 나눈 종류: 정규직, 인턴·연수, 박사후·연수연구원, 비정규·기타, 기타 |
| job_types | 제목에 드러난 직군: 연구, 기술, 행정 (없으면 빈 목록) |
| degrees / degree_note | 지원 학위와 설명. 클로드가 공고문으로 확인해 채움. `null` = 확인 전, `[]` = 학력 무관·요건 없음(위젯에 「학력 무관」) |
| checked_by / checked_at / evidence | 클로드 확인 표시, 시각, 확인한 곳. 있어야 캘린더(items)에 뜸 |
| start / end | 접수 시작일 / 마감일 (한국 날짜) |
| status | 접수 중 / 접수 전 / 마감(이번 달에 마감된 공고, 달이 바뀌면 빠짐. 위젯은 달력에 회색으로만 그림) |
| url | 공고 원문 주소 |
| source | fairy, nst, applyin |
| column_url / column_title | 「칼럼」 버튼에 붙일 글을 클로드가 직접 고른 경우의 주소·제목. 없으면 위젯이 `jcy_columns.json`으로 고름 |

- 마감일이 지난 공고는 그달 말까지 status 「마감」으로 남고, 다음 달 첫 수집 때 빠집니다(대표님 지시 2026-11-10). 발표일은 넣지 않습니다.
- `pending`: 자동 수집했지만 클로드 확인 전인 공고(`reasons`에 확인할 것). 캘린더에 띄우지 않습니다. 원문으로 확인되지 않은 이유는 `check_note`(다음 수집 뒤에도 남음).
- `excluded`: 클로드가 점검에서 뺀 공고(`reason`, `excluded_by`, `excluded_at`). 자동 수집이 다시 `pending`에 넣지 않고, 마감일이 지나면 지웁니다.
- `review_queue`: 누리집 게시판에서 새로 찾은 글(30일 보관). 클로드가 확인한 뒤 캘린더에 반영합니다.
- `jcy_columns.json`: 기관별 관련 칼럼 연결표(칼럼 게시판 /66 제목에 기관 이름·약칭이 있는 글, 최신순). `build_column_map.py`로 만든다.
- `sci_calendar.json`: 정출연 밖 과학기술 공공기관 28곳(`orgs_sci.json`) 자료. 형식은 같고, 공고마다 `group`(사업발주·싱크탱크 / 국책연구소 / 원자력 안전 / 전문연구소·시험기관·국방)이 있다. `source`는 alio, applyin, board.
- 확인 절차는 `CHECK.md`.
