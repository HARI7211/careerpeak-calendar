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
| status | 접수 중 / 접수 전 |
| url | 공고 원문 주소 |
| source | fairy, nst, applyin |

- 마감일이 지난 공고는 자동으로 빠집니다. 발표일은 넣지 않습니다.
- `pending`: 자동 수집했지만 클로드 확인 전인 공고(`reasons`에 확인할 것). 캘린더에 띄우지 않습니다. 원문으로 확인되지 않은 이유는 `check_note`(다음 수집 뒤에도 남음).
- `excluded`: 클로드가 점검에서 뺀 공고(`reason`, `excluded_by`, `excluded_at`). 자동 수집이 다시 `pending`에 넣지 않고, 마감일이 지나면 지웁니다.
- `review_queue`: 누리집 게시판에서 새로 찾은 글(30일 보관). 클로드가 확인한 뒤 캘린더에 반영합니다.
- 확인 절차는 `CHECK.md`.
