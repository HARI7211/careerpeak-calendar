# -*- coding: utf-8 -*-
"""정출연 밖 과학기술 공공기관 28곳 채용 공고 수집 (data/orgs_sci.json).
- ALIO 진행중 목록(job.alio.go.kr): 기관 이름이 같은 공고
- applyin: KTR·ADD
- 누리집 게시판 새 글: BOARDS → review_queue
- 브라우저로만 열리는 곳(KOPRI·KBRI·NNFC·KATECH·KETEP 등)은 수집하지 않는다. 클로드 점검이 화·목 과기공공 작업 기록으로 보탠다.
결과: data/sci_calendar.json(jcy_calendar.json과 같은 형식), 상태: data/seen_boards_sci.json
"""
import json, os, re, time, urllib.request, urllib.parse, http.cookiejar, html
from datetime import datetime, timedelta
from fetch import KST, ROOT, category, job_types

UA = {"User-Agent": "Mozilla/5.0"}  # 몇몇 기관은 이 값만 받는다(조회경로 정본 0-2)
APPLYIN = {"KTR": "ktr", "ADD": "add"}
BOARDS = {
    "STEPI": "https://www.stepi.re.kr/site/stepiko/ex/bbs/List.do?cbIdx=1252",
    "KEIT": "https://www.keit.re.kr/board.es?mid=a10307020000&bid=0046",
    "KIDA": "https://www.kida.re.kr/frt/board/frtNormalBoard.do?sidx=1125&depth=2",
    "KRISO": "https://www.kriso.re.kr/board.es?mid=a10402030000&bid=0012",
    "KRISO공지": "https://www.kriso.re.kr/board.es?mid=a10401000000&bid=0010",
    "KANC": "https://www.kanc.re.kr/gnb04/snb02_02.do",
    "KINS": "https://www.kins.re.kr/recru-bord",
    "KINAC": "https://www.kinac.re.kr/board?menuId=MN0000000498&siteId=00002",
    "KETI": "https://www.keti.re.kr/notice/employment.php",
    "KOPTI": "https://www.kopti.re.kr/ko/notice/employ.do",
    "KICET": "https://www.kicet.re.kr/00020/00117/00253.web",
    "KTL": "https://www.ktl.re.kr/notice/notice_2/menu1/notice_announcement.do",
    "KCL": "https://www.kcl.re.kr/site/program/board/basicboard/list.do?boardtypeid=88&menuid=001016006001",
    "KTC": "https://www.ktc.re.kr/web_united/board/list_season_02.asp?pagen=701",
}
# ALIO에 기관 이름이 「한국해양과학기술원」으로 올라오지만 제목으로 부설기관을 가린다
ALIO_SUB = {"한국해양과학기술원": [("선박해양플랜트연구소", "KRISO"), ("극지연구소", "KOPRI")]}


def get(url, data=None, accept=None, opener=None):
    h = dict(UA)
    if accept:
        h["Accept"] = accept
        h["X-Requested-With"] = "XMLHttpRequest"
    req = urllib.request.Request(url, data=data, headers=h)
    with (opener or urllib.request.build_opener()).open(req, timeout=25) as r:
        return r.read()


def text(raw):
    for enc in ("utf-8", "euc-kr"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", "replace")


def main():
    orgs = json.load(open(os.path.join(ROOT, "data/orgs_sci.json"), encoding="utf-8"))["orgs"]
    by_name = {o["name"]: o for o in orgs}
    by_short = {o["short"]: o for o in orgs}
    now = datetime.now(KST)
    today = now.strftime("%Y-%m-%d")
    items, errors = [], []

    def add(short, sid, t, start, end, status, url, source):
        o = by_short[short]
        items.append({"id": f"{short}-{sid}", "org": o["name"], "org_short": short, "group": o["group"], "title": t,
                      "category": category(t), "job_types": job_types(t), "degrees": None,
                      "start": start, "end": end, "status": status, "url": url, "source": source})

    # ALIO 진행중 목록
    try:
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        op.addheaders = [("Referer", "https://job.alio.go.kr/recruit.do")]
        for p in range(1, 200):
            body = urllib.parse.urlencode([("pageNo", p), ("ing", "2"), ("s_date", ""), ("e_date", "")]).encode()
            s = text(get("https://job.alio.go.kr/recruit.do", data=body, opener=op))
            trs = re.findall(r'<tr>\s*<td style="border-left.*?</tr>', s, re.S)
            if not trs:
                break
            for tr in trs:
                idx = re.search(r"recruitview.do\?idx=(\d+)", tr).group(1)
                td = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
                t, org, reg, dl = td[2], td[3], td[6], td[7]
                if org not in by_name:
                    continue
                short = by_name[org]["short"]
                for word, sub in ALIO_SUB.get(org, []):
                    if word in t:
                        short = sub
                start = reg.replace(".", "-") if re.match(r"\d{4}\.\d\d\.\d\d$", reg) else None
                m = re.match(r"(\d\d)\.(\d\d)\.(\d\d)", dl)
                end = f"20{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None
                add(short, f"alio{idx}", t, start, end, "접수 전" if start and start > today else "접수 중",
                    f"https://job.alio.go.kr/recruitview.do?idx={idx}", "alio")
            time.sleep(0.5)
    except Exception as e:
        errors.append(f"ALIO: {e}")

    # applyin
    def kst(s):
        return datetime.fromisoformat(s.replace("Z", "+00:00").split(".")[0] + "+00:00").astimezone(KST).strftime("%Y-%m-%d") if s else None
    for short, sub in APPLYIN.items():
        try:
            for x in json.loads(get(f"https://{sub}.applyin.co.kr/jobs", accept="application/json"))["data"]:
                if (x.get("status") or {}).get("code") not in ("ing", "ready", "wait"):
                    continue
                add(short, x["id"], x["title"].strip(), kst(x.get("start")), kst(x.get("end")),
                    "접수 중" if x["status"]["code"] == "ing" else "접수 전", f"https://{sub}.applyin.co.kr/jobs/{x['id']}", "applyin")
        except Exception as e:
            errors.append(f"{short} applyin: {e}")

    items = [i for i in items if not i["end"] or i["end"] >= today]
    # 공개(items)·대기(pending)·제외(excluded) 나누기: fetch.py와 같은 규칙
    cp = os.path.join(ROOT, "data/sci_calendar.json")
    prev = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    published = {i["id"]: i for i in prev.get("items", []) if i.get("checked_by")}
    prev_pending = {i["id"]: i for i in prev.get("pending", [])}
    excluded = {i["id"]: i for i in prev.get("excluded", [])}
    pub, pend = [], []
    for it in items:
        if it["id"] in published:
            keep = dict(published[it["id"]])
            for k in ("title", "start", "end", "status", "url"):
                if keep.get(k) != it[k]:
                    keep.setdefault("changed", []).append(k)
                keep[k] = it[k]
            pub.append(keep)
        elif it["id"] in excluded:
            continue
        else:
            reasons = ["지원 학위 확인 필요"]
            if not it["start"] or not it["end"]:
                reasons.append("접수 기간 없음")
            if it["category"] == "기타":
                reasons.append("종류 분류 안 됨")
            if not it["job_types"]:
                reasons.append("직군 제목에 없음")
            it["reasons"] = reasons
            it["found_at"] = prev_pending.get(it["id"], {}).get("found_at", today)
            if prev_pending.get(it["id"], {}).get("check_note"):
                it["check_note"] = prev_pending[it["id"]]["check_note"]
            pend.append(it)
    # 클로드가 게시판 글로 직접 넣은 공개 항목(source board)은 마감 전까지 남긴다.
    # 이번 달에 마감된 공개 공고는 출처와 상관없이 status "마감"으로 달이 바뀔 때까지 남긴다(대표님 지시 2026-11-10)
    pub_ids = {i["id"] for i in pub}
    for i in published.values():
        if i["id"] in pub_ids:
            continue
        if i.get("end") and i["end"] < today:
            if i["end"][:7] == today[:7]:
                keep = dict(i)
                keep["status"] = "마감"
                pub.append(keep)
        elif i.get("source") not in ("alio", "applyin"):
            pub.append(i)
    pub.sort(key=lambda i: (i["end"] or "9999", i["org_short"]))
    pend.sort(key=lambda i: (i["end"] or "9999", i["org_short"]))
    excl = sorted((x for x in excluded.values() if not x.get("end") or x["end"] >= today), key=lambda i: (i.get("end") or "9999", i.get("org_short", "")))

    # 누리집 게시판 새 글 → review_queue
    sp = os.path.join(ROOT, "data/seen_boards_sci.json")
    seen = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    queue = []
    for key, url in BOARDS.items():
        short = re.sub(r"[^A-Z]", "", key)
        time.sleep(1)
        try:
            raw = text(get(url))
        except Exception as e:
            errors.append(f"{key} 게시판: {e}")
            continue
        titles = []
        for a in re.findall(r"<a[^>]*>(.*?)</a>", raw, re.S):
            t = html.unescape(re.sub(r"<[^>]+>|\s+", " ", a)).strip()
            if 8 <= len(t) <= 120 and re.search(r"채용|모집|공고", t) and t not in titles:
                titles.append(t)
        old = set(seen.get(key, []))
        if old:
            for t in titles:
                if t not in old:
                    queue.append({"org_short": short, "org": by_short[short]["name"], "group": by_short[short]["group"], "title": t,
                                  "board": url, "reason": "누리집 게시판 새 글", "found_at": today})
        seen[key] = sorted(set(titles) | old)[-300:]
    json.dump(seen, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    old_q = [q for q in prev.get("review_queue", []) if q.get("found_at", "") >= (now - timedelta(days=30)).strftime("%Y-%m-%d")]
    out = {"version": 1, "updated_at": now.isoformat(timespec="seconds"), "month": now.strftime("%Y-%m"),
           "note": "정출연 밖 과학기술 공공기관 28곳(data/orgs_sci.json). 캘린더는 items만 띄운다. items = 클로드가 원문으로 확인해 공개한 것. pending = 자동 수집했지만 확인 전. review_queue = 누리집 게시판 새 글. errors = 열리지 않은 출처. excluded = 클로드가 점검에서 뺀 공고. 브라우저로만 열리는 곳은 클로드 점검이 보탠다.",
           "items": pub, "pending": pend, "review_queue": old_q + queue, "errors": errors, "excluded": excl}
    json.dump(out, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"sci items {len(pub)}, pending {len(pend)}, review_queue +{len(queue)}, errors {len(errors)}, excluded {len(excl)}")
    for e in errors:
        print("  error:", e)


if __name__ == "__main__":
    main()
