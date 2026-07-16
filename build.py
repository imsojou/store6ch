# -*- coding: utf-8 -*-
"""
상권분석지도.html 재빌드 스크립트
─────────────────────────────────────────────
data/stores.json + data/apts.json 을 data/앱템플릿_shell.html 에 주입해
상권분석지도.html 을 새로 만듭니다.

[사용법]
1. data/stores.json (매장) 또는 data/apts.json (입주단지) 을 수정
2. 이 파일과 같은 폴더에서 build.bat 더블클릭 (또는 python build.py)
3. 상권분석지도.html 이 갱신됨 → 바로가기로 열면 반영됨
"""
import json, os, sys, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
TPL  = os.path.join(DATA, "앱템플릿_shell.html")
OUT  = os.path.join(HERE, "상권분석지도.html")

def die(msg):
    print("\n[오류] " + msg)
    input("\n엔터를 누르면 닫힙니다...")
    sys.exit(1)

# 1) 필수 파일 확인
for p in (TPL, os.path.join(DATA,"stores.json"), os.path.join(DATA,"apts.json")):
    if not os.path.exists(p):
        die("파일이 없습니다: " + p)

# 2) JSON 유효성 검사 (깨진 데이터로 빌드 방지)
try:
    stores = json.load(open(os.path.join(DATA,"stores.json"), encoding="utf-8"))
    apts   = json.load(open(os.path.join(DATA,"apts.json"),   encoding="utf-8"))
except Exception as e:
    die("JSON 형식 오류: " + str(e))

n_store = len(stores.get("stores", []))
n_apt   = len(apts.get("apts", []))
if n_store == 0: die("stores.json 에 매장이 없습니다.")

# 3) 템플릿에 주입
html = open(TPL, encoding="utf-8").read()
if "__DATA__" not in html or "__APT__" not in html:
    die("템플릿에 __DATA__ / __APT__ 자리표시자가 없습니다. 앱템플릿_shell.html 을 확인하세요.")

sdata = json.dumps(stores, ensure_ascii=False, separators=(",",":"))
sapt  = json.dumps(apts,   ensure_ascii=False, separators=(",",":"))
html = html.replace("__DATA__", sdata).replace("__APT__", sapt)

# 4) 기존 파일 백업 후 저장
if os.path.exists(OUT):
    bak = os.path.join(HERE, "backup")
    os.makedirs(bak, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(OUT, os.path.join(bak, f"상권분석지도_{stamp}.html"))

open(OUT, "w", encoding="utf-8").write(html)

print("=" * 44)
print("  재빌드 완료")
print("=" * 44)
print(f"  매장       : {n_store:,} 개")
print(f"  입주단지   : {n_apt:,} 개")
print(f"  파일 크기  : {os.path.getsize(OUT)//1024:,} KB")
print(f"  저장 위치  : {OUT}")
print("  (기존 파일은 backup 폴더에 보관됨)")
print("=" * 44)
input("\n엔터를 누르면 닫힙니다...")
