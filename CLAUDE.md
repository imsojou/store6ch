# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A single-file, offline-first web app: **전국 가전 유통 상권분석 지도** (nationwide commercial-district analysis map for Korean electronics retail). The entire app — HTML, CSS, JS, and all data — lives in `상권분석지도.html` (~788KB). Users open it by double-clicking; there is no server, no backend, no build pipeline beyond a data-injection script, and no package manager. Only map tiles and CDN libraries load online.

All documentation and UI text is in **Korean**. Keep it that way. All files are UTF-8.

## Repository layout

| File | Role |
|---|---|
| `상권분석지도.html` | The app itself, with data embedded. This is the deliverable. |
| `build.py` / `build.bat` | Rebuild script: injects JSON data into an HTML template (see below). `build.bat` is the Windows double-click wrapper. |
| `README.md` | Data inventory, sources, channel/team domain rules, folder structure. |
| `업데이트_방법.md` | End-user instructions for the four data-update paths. |
| `AI스튜디오_제작가이드.md` | Guide for recreating the app via Google AI Studio; also the most complete written **spec** of the app's features, data schema, and calculation rules. |

**Important:** the `data/` and `source/` folders referenced by `build.py` and the README (`data/stores.json`, `data/apts.json`, `data/앱템플릿_shell.html`, CSV sources) are **not committed to this repo** — they exist only on the maintainer's machine. Therefore `python build.py` will fail here with a missing-file error. In this repo, changes to app behavior or data must be made by **editing `상권분석지도.html` directly**.

## Build / test / lint

- Rebuild (only works where `data/` exists): `python build.py` or double-click `build.bat` on Windows. It validates both JSON files, replaces the `__DATA__` and `__APT__` placeholders in `data/앱템플릿_shell.html`, backs up the previous output to `backup/`, and writes `상권분석지도.html`.
- There are no tests, no linter, and no dependencies to install. To verify a change, open `상권분석지도.html` in a browser (internet needed for map tiles/CDNs) and exercise the affected feature.
- CDN libraries (pinned in the HTML `<head>`): Leaflet 1.9.4, Leaflet.markercluster 1.5.3, leaflet.heat 0.2.0, Chart.js 4.4.1. Do not add other storage or backends — **localStorage is the only persistence**.

## Architecture

The app is a **data snapshot** design:

1. Template (`앱템플릿_shell.html`) contains the app code plus `__DATA__` / `__APT__` placeholders inside `<script type="application/json">` tags.
2. `build.py` injects minified `stores.json` (1,314 stores + region→team mapping in `meta.regionTeam`) and `apts.json` (675 upcoming apartment complexes) into those placeholders.
3. At runtime, user edits (직영/대리점 corrections, team reassignments, store metrics like 평수/직원수/매출) are stored **only in the browser's localStorage** and exported/imported via CSV in the 내보내기 tab. Permanent changes require merging those CSVs back into `stores.json` and rebuilding.

`상권분석지도.html` has only ~1,400 lines because the embedded JSON is minified onto single very long lines — use targeted search rather than reading the whole file, and be careful not to corrupt the JSON lines when editing.

### Data schema (embedded JSON)

`stores` records: `id` (SS-/LG-/HM-/EM- prefix + 4 digits), `ch` (channel), `nm` (name), `ty` (매장유형: 가전종합·모바일전문·사업장內), `lt` (입점유형: 로드샵·백화점·대형마트숍인숍·전자관·아울렛), `sd`/`sg`/`em` (시도/시군구/읍면동), `ad` (address), `la`/`ln` (coords), `tm` (지역팀), `mt` (`"대형팀"` or `""`), `c3` (competitors within 3km), `nd` (nearest-competitor distance, m).

`apts` records: `nm`, `ym` (입주예정월), `hh` (세대수), `ty` (분양/임대/조합), `ad`, `sd`, `sg`, `la`/`ln`, `pr` (coordinate precision — 법정동 center, up to ~1km error).

## Domain rules (do not break these)

- **Six channels** with fixed brand colors and marker initials: 삼성직영 SS `#1428A0`, 삼성대리점 SDP `#00AEEF`, 베스트샵직영 BS `#A50034`, 베스트샵대리점 BSD `#EC6C8C`, 롯데하이마트 HM `#ED1C24`, 일렉트로마트 EM `#FFD400` (black text).
- **Two overlapping team systems**: every store belongs to exactly one of 7 지역팀 (assigned per 시군구, based on Samsung stores); separately, 대형팀 covers the 63 Samsung stores located inside 일렉트로마트 (`mt === "대형팀"`). These are **double-counted on purpose** — 대형팀 totals must never be added into 지역팀 sums. The 73 일렉트로마트 stores themselves are a competitor channel, not 대형팀.
- Samsung stores whose name contains `일렉트로마트` are **always 삼성직영** — the UI blocks reclassifying them as 대리점.
- Team reassignment is only exposed on Samsung store popups, and moves **the entire 시군구** (all channels) via the `meta.regionTeam` key `시도|시군구`.
- Marker clustering is **per-channel**: 6 independent cluster groups; channels never merge into one cluster.
- 점유율 (share) calculations must reuse the same filter pass as the map (all sidebar filters apply to the denominator); default denominator excludes 일렉트로마트. "열세" highlighting = region share < overall average − 5%p.
- Distances use Haversine with Earth radius 6,371,000m, integer meters. 기회점수 = 세대수 ÷ nearest own-store distance (km).

## Data update workflows (from 업데이트_방법.md)

1. Small corrections (classification, team, store metrics): done in-app, localStorage only — remind users to export CSV backups.
2. Store openings/closings: edit `stores.json` → rebuild.
3. Apartment data: refreshed semiannually from 한국부동산원 (공공데이터포털 dataset 15111714); replace `apts.json` → rebuild. Temporary additions possible via in-app CSV upload.
4. Making in-app edits permanent: merge exported CSVs into `stores.json` (`ch`, `tm`, `meta.regionTeam`) → rebuild.
