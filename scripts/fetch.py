# -*- coding: utf-8 -*-
"""정출연 25곳 채용 공고 수집 (API 키·로그인·브라우저 없이).
- 24곳: https://{sub}.fairy.im/api/company/announcements
- KARI: https://kari.applyin.co.kr/jobs (Accept: application/json)
- NST 공동채용: https://onest.fairy.im/api/company/announcements (기관 목록에 없는 것만 보탬)
- fairy 목록이 비거나 상시 인재풀만 있는 곳(KRRI·KFRI·KIMS·KFE·NIGT·KIER)은 누리집 게시판에서 새 글만 찾아 review_queue에 넣는다.
결과: data/jcy_calendar.json, 상태: data/seen_boards.json
"""
import json, os, re, sys, time, urllib.request, html
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0 (careerpeak-calendar; +https://www.careerpeak.co.kr)"}
FAIRY = {"kist": "KIST", "kbsi": "KBSI", "kasi": "KASI", "kribb": "KRIBB", "kisti": "KISTI", "kiom": "KIOM", "kitech": "KITECH", "etri": "ETRI", "nsr": "NSR", "kict": "KICT", "krri": "KRRI", "kriss": "KRISS", "kfri": "KFRI", "wikim": "WIKIM", "kigam": "KIGAM", "kimm": "KIMM", "kims": "KIMS", "kier": "KIER", "keri": "KERI", "krict": "KRICT", "kit": "KIT", "kaeri": "KAERI", "kfe": "KFE", "nigt": "NIGT"}
NST_PREFIX = {"기초연": "KBSI", "ETRI": "ETRI", "한국원자력연구원": "KAERI", "원자력연": "KAERI", "생명연": "KRIBB", "지자연": "KIGAM", "건설연": "KICT", "녹색연": "NIGT", "국보연": "NSR", "화학연": "KRICT", "표준연": "KRISS", "KISTI": "KISTI", "전기연": "KERI", "재료연": "KIMS", "철도연": "KRRI", "김치연": "WIKIM", "한국생산기술연구원": "KITECH", "생기원": "KITECH", "한의학연": "KIOM", "식품연": "KFRI", "기계연": "KIMM", "에너지연": "KIER", "핵융합연": "KFE", "독성연": "KIT", "천문연": "KASI", "KIST": "KIST"}
BOARDS = {"KRRI": "https://www.krri.re.kr/web/contents/krri030502.do", "KFRI": "https://kfri.re.kr/web/board/13/postList", "KIMS": "https://www.kims.re.kr/v17/bbx/board.php?bx_table=03_05", "KFE": "https://www.kfe.re.kr/board.es?mid=a10304010000&bid=0013", "NIGT": "https://www.nigt.re.kr/gtck/recruit.do", "KIER": "https://www.kier.re.kr/board?menuId=MENU00459"}


def get(url, accept=None):
    h = dict(UA)
    if accept:
        h["Accept"] = accept
        h["X-Requested-With"] = "XMLHttpRequest"
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def category(t):
    if "비정규" in t:
        return "비정규·기타"
    if re.search(r"정규직|정직원", t):
        return "정규직"
    if re.search(r"박사후|석사후|연수연구원|post-?doc|포닥", t, re.I):
        return "박사후·연수연구원"
    if re.search(r"인턴|연수생|연수직|현장실습", t):
        return "인턴·연수"
    if re.search(r"기간제|계약직|위촉|육아휴직|대체인력|인재풀|별정직|특수사업직|무기계약", t):
        return "비정규·기타"
    if re.search(r"공개채용|신입직원|공개경쟁|공동채용|직원 채용", t):
        return "정규직"
    return "기타"


def job_types(t):
    out = []
    if re.search(r"연구직|연구분야|연구 분야|연구\s*,", t):
        out.append("연구")
    if re.search(r"기술직|기능직|기술\s*\)", t):
        out.append("기술")
    if re.search(r"행정|경영", t):
        out.append("행정")
    return out


def day(s):
    return s[:10] if s else None


def main():
    orgs = {o["short"]: o["name"] for o in json.load(open(os.path.join(ROOT, "data/orgs.json"), encoding="utf-8"))["orgs"]}
    now = datetime.now(KST)
    today = now.strftime("%Y-%m-%d")
    items, errors = [], []
    seen_keys = set()
    for sub, short in FAIRY.items():
        try:
            d = json.loads(get(f"https://{sub}.fairy.im/api/company/announcements"))
        except Exception as e:
            errors.append(f"{short}: {e}")
            continue
        for x in d:
            if x.get("applicationStatus") not in ("inProgress", "readyApplication"):
                continue
            if x.get("projectDivision") == "always":
                continue
            t = x["title"].strip()
            it = {"id": f"{short}-{x['id']}", "org": orgs.get(short, short), "org_short": short, "title": t,
                  "category": category(t), "job_types": job_types(t), "degrees": None,
                  "start": day(x.get("applicationBeginAt")), "end": day(x.get("applicationEndAt")),
                  "status": "접수 중" if x["applicationStatus"] == "inProgress" else "접수 전",
                  "url": f"https://{sub}.fairy.im/announcement/detail/{x['id']}", "source": "fairy"}
            items.append(it)
            seen_keys.add((short, it["start"], it["end"]))
        time.sleep(2)
    # NST 공동채용: 기관 목록에 없는 것만
    try:
        for x in json.loads(get("https://onest.fairy.im/api/company/announcements")):
            if x.get("applicationStatus") not in ("inProgress", "readyApplication"):
                continue
            t = x["title"].strip()
            m = re.match(r"\s*\(([^)]*)\)", t)
            short = NST_PREFIX.get(m.group(1).strip()) if m else None
            if not short:
                continue
            key = (short, day(x.get("applicationBeginAt")), day(x.get("applicationEndAt")))
            if key in seen_keys:
                continue
            items.append({"id": f"NST-{x['id']}", "org": orgs.get(short, short), "org_short": short, "title": t,
                          "category": category(t), "job_types": job_types(t), "degrees": None,
                          "start": key[1], "end": key[2], "status": "접수 중" if x["applicationStatus"] == "inProgress" else "접수 전",
                          "url": f"https://onest.fairy.im/announcement/detail/{x['id']}", "source": "nst"})
            seen_keys.add(key)
    except Exception as e:
        errors.append(f"NST: {e}")
    time.sleep(2)
    # KARI (시각은 UTC → 한국 날짜)
    try:
        for x in json.loads(get("https://kari.applyin.co.kr/jobs", accept="application/json"))["data"]:
            if (x.get("status") or {}).get("code") not in ("ing", "ready", "wait"):
                continue
            def kst(s):
                return datetime.fromisoformat(s.replace("Z", "+00:00").split(".")[0] + "+00:00").astimezone(KST).strftime("%Y-%m-%d") if s else None
            t = x["title"].strip()
            items.append({"id": f"KARI-{x['id']}", "org": orgs.get("KARI", "한국항공우주연구원"), "org_short": "KARI", "title": t,
                          "category": category(t), "job_types": job_types(t), "degrees": None,
                          "start": kst(x.get("start")), "end": kst(x.get("end")), "status": "접수 중" if x["status"]["code"] == "ing" else "접수 전",
                          "url": f"https://kari.applyin.co.kr/jobs/{x['id']}", "source": "applyin"})
    except Exception as e:
        errors.append(f"KARI: {e}")
    items = [i for i in items if not i["end"] or i["end"] >= today]
    # 공개(items)와 확인 대기(pending) 나누기: 클로드가 보충해 공개한 항목만 items에 남긴다
    cp0 = os.path.join(ROOT, "data/jcy_calendar.json")
    prev0 = json.load(open(cp0, encoding="utf-8")) if os.path.exists(cp0) else {}
    published = {i["id"]: i for i in prev0.get("items", []) if i.get("checked_by")}
    prev_pending = {i["id"]: i for i in prev0.get("pending", [])}
    pub, pend = [], []
    for it in items:
        if it["id"] in published:
            keep = dict(published[it["id"]])
            for k in ("title", "start", "end", "status", "url"):
                if keep.get(k) != it[k]:
                    keep.setdefault("changed", []).append(k)
                keep[k] = it[k]
            pub.append(keep)
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
            pend.append(it)
    items = sorted(pub, key=lambda i: (i["end"] or "9999", i["org_short"]))
    pend.sort(key=lambda i: (i["end"] or "9999", i["org_short"]))
    # 누리집 게시판 새 글 → review_queue
    sp = os.path.join(ROOT, "data/seen_boards.json")
    seen = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    queue = []
    for short, url in BOARDS.items():
        time.sleep(2)
        try:
            raw = get(url).decode("utf-8", "replace")
        except Exception as e:
            errors.append(f"{short} 게시판: {e}")
            continue
        titles = []
        for a in re.findall(r"<a[^>]*>(.*?)</a>", raw, re.S):
            t = html.unescape(re.sub(r"<[^>]+>|\s+", " ", a)).strip()
            if 8 <= len(t) <= 120 and re.search(r"채용|모집|공고", t) and t not in titles:
                titles.append(t)
        old = set(seen.get(short, []))
        if old:
            for t in titles:
                if t not in old:
                    queue.append({"org_short": short, "org": orgs.get(short, short), "title": t, "board": url, "reason": "누리집 게시판 새 글", "found_at": today})
        seen[short] = sorted(set(titles) | old)[-300:]
    json.dump(seen, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cp = os.path.join(ROOT, "data/jcy_calendar.json")
    prev = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    old_q = [q for q in prev.get("review_queue", []) if q.get("found_at", "") >= (now - timedelta(days=30)).strftime("%Y-%m-%d")]
    out = {"version": 2, "updated_at": now.isoformat(timespec="seconds"), "month": now.strftime("%Y-%m"),
           "note": "캘린더는 items만 띄운다. items = 클로드가 공고 원문으로 학위·직군을 확인해 공개한 것(checked_by 있음). pending = 자동 수집했지만 확인 전. review_queue = 누리집 게시판 새 글(확인 전). errors = 열리지 않은 출처(클로드가 다른 길로 확인).",
           "items": items, "pending": pend, "review_queue": old_q + queue, "errors": errors}
    json.dump(out, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"items {len(items)}, pending {len(pend)} (정규직 {sum(i['category']=='정규직' for i in pend)}), review_queue +{len(queue)}, errors {len(errors)}")
    for e in errors:
        print("  error:", e)


if __name__ == "__main__":
    main()
