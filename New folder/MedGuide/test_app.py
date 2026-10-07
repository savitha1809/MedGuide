"""
MedGuide — Full Functionality Test Suite
Tests: Home, Search, Category, Detail, Admin, Add, Delete, Edge Cases
"""
import urllib.request
import urllib.parse
import urllib.error
import re
import sys
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:5000"
PASS_COUNT = 0
FAIL_COUNT = 0
FAILURES = []


def check(label, path, expected_status=200, must_contain=None, must_not_contain=None):
    global PASS_COUNT, FAIL_COUNT
    try:
        resp = urllib.request.urlopen(BASE + path, timeout=6)
        status = resp.getcode()
        body = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        status = e.code
        body = ""
    except Exception as e:
        FAIL_COUNT += 1
        msg = f"[FAIL] {label} → {e}"
        print(msg); FAILURES.append(msg)
        return ""

    issues = []
    if status != expected_status:
        issues.append(f"HTTP {status} (expected {expected_status})")
    for kw in (must_contain or []):
        if kw.lower() not in body.lower():
            issues.append(f'missing "{kw}"')
    for kw in (must_not_contain or []):
        if kw.lower() in body.lower():
            issues.append(f'unexpected "{kw}"')

    if issues:
        FAIL_COUNT += 1
        msg = f"  [FAIL] {label}  →  {', '.join(issues)}"
        print(msg); FAILURES.append(msg)
    else:
        PASS_COUNT += 1
        print(f"  [PASS] {label}")
    return body


def post(label, path, data):
    global PASS_COUNT, FAIL_COUNT
    try:
        payload = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(BASE + path, data=payload, method="POST")

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a): return None

        opener = urllib.request.build_opener(NoRedirect())
        try:
            resp = opener.open(req, timeout=6)
            status = resp.getcode()
        except urllib.error.HTTPError as e:
            status = e.code
    except Exception as e:
        FAIL_COUNT += 1
        msg = f"  [FAIL] {label} → {e}"
        print(msg); FAILURES.append(msg)
        return

    if status in (200, 302, 303):
        PASS_COUNT += 1
        print(f"  [PASS] {label}  →  HTTP {status} (redirect OK)")
    else:
        FAIL_COUNT += 1
        msg = f"  [FAIL] {label}  →  HTTP {status}"
        print(msg); FAILURES.append(msg)


# ══════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("   MedGuide — Full Functionality Test Suite")
print("=" * 60)

# ── 1. HOME PAGE
print("\n[1] HOME PAGE")
check("GET /",                "/",  must_contain=["MedGuide", "Search"])
check("Has medicine cards",   "/",  must_contain=["Paracetamol", "Cetirizine", "Ibuprofen"])
check("Has category links",   "/",  must_contain=["Tablets", "Syrups", "Ointments", "Capsules"])
check("Has footer/disclaimer","/",  must_contain=["2026", "educational"])

# ── 2. SEARCH
print("\n[2] SEARCH")
check("Search exact: Paracetamol",    "/search?medicine=Paracetamol",  must_contain=["Paracetamol"],  must_not_contain=["No medicine found"])
check("Search partial: para",         "/search?medicine=para",          must_contain=["Paracetamol"])
check("Search by category: Tablet",   "/search?medicine=Tablet",        must_contain=["Tablet"])
check("Search by composition: 500mg", "/search?medicine=500mg",         must_contain=["500mg"])
check("Search no result: zzzz",       "/search?medicine=zzzxyz",        must_contain=["No medicine found"])
check("Search Ibuprofen",             "/search?medicine=Ibuprofen",     must_contain=["Ibuprofen"])
check("Search Amoxicillin",           "/search?medicine=Amoxicillin",   must_contain=["Amoxicillin"])

# ── 3. CATEGORIES
print("\n[3] CATEGORY FILTER")
check("Tablet category",   "/category/Tablet",   must_contain=["Paracetamol", "Ibuprofen"])
check("Capsule category",  "/category/Capsule",  must_contain=["Amoxicillin", "Omeprazole"])
check("Syrup category",    "/category/Syrup",    must_contain=["Syrup"])
check("Ointment category", "/category/Ointment", must_contain=["Mupirocin", "Clotrimazole"])
check("Unknown category",  "/category/Unknown",  must_contain=["found"])

# ── 4. MEDICINE DETAIL PAGES
print("\n[4] MEDICINE DETAIL PAGES")
check("Detail ID=1",              "/medicine/1",    must_contain=["Composition", "Uses", "Precautions", "Side Effects", "Warnings", "Back"])
check("Detail ID=2",              "/medicine/2",    must_contain=["Composition"])
check("Detail ID=3",              "/medicine/3",    must_contain=["Composition"])
check("Detail: 404 for bad ID",   "/medicine/9999", expected_status=404)
check("Detail has disclaimer",    "/medicine/1",    must_contain=["Medical Disclaimer"])

# ── 5. ADMIN
print("\n[5] ADMIN PAGE")
check("GET /admin",         "/admin", must_contain=["Admin", "Add New Medicine"])
check("Admin has table",    "/admin", must_contain=["Medicine List", "Medicine Name", "Category"])
check("Admin form fields",  "/admin", must_contain=["composition", "side_effects", "warnings"])

# ── 6. ADD MEDICINE
print("\n[6] ADD MEDICINE")
post("POST /add — valid data", "/add", {
    "medicine_name": "TestMedQA",
    "category":      "Tablet",
    "composition":   "TestCompound 99mg",
    "uses":          "Quality assurance testing",
    "purpose":       "QA validation",
    "precautions":   "None for testing",
    "side_effects":  "None",
    "warnings":      "Test only",
})
check("New med in admin list",   "/admin",                        must_contain=["TestMedQA"])
check("New med is searchable",   "/search?medicine=TestMedQA",    must_contain=["TestMedQA"])
check("New med shows in home",   "/",                             must_contain=["TestMedQA"])

# ── 7. DETAIL PAGE OF ADDED MEDICINE
print("\n[7] NEW MEDICINE DETAIL")
admin_body = urllib.request.urlopen(BASE + "/admin", timeout=5).read().decode()
ids = re.findall(r'del-(\d+)', admin_body)
new_id = ids[0] if ids else None

if new_id:
    check(f"Detail page ID={new_id}", f"/medicine/{new_id}",
          must_contain=["TestMedQA", "TestCompound 99mg", "Quality assurance"])
else:
    FAIL_COUNT += 1
    FAILURES.append("  [FAIL] Could not find new medicine ID in admin page")
    print("  [FAIL] Could not find new medicine ID in admin page")

# ── 8. DELETE MEDICINE
print("\n[8] DELETE MEDICINE")
if new_id:
    post(f"POST /delete/{new_id}", f"/delete/{new_id}", {})
    check("Med gone from admin after delete", "/admin",  must_not_contain=["TestMedQA"])
    check("Med gone from search after delete", "/search?medicine=TestMedQA", must_contain=["No medicine found"])
else:
    FAIL_COUNT += 1
    print("  [FAIL] Skipped — no ID found")

# ── 9. STATIC FILES
print("\n[9] STATIC FILES")
check("CSS file loads",     "/static/style.css", must_contain=[":root", "--bg", "Inter"])

# ── 10. NAVIGATION LINKS IN HTML
print("\n[10] NAVIGATION & LINKS")
home = urllib.request.urlopen(BASE + "/", timeout=5).read().decode()
nav_links = re.findall(r'href=["\']([^"\']+)["\']', home)
check("Home link present in nav",  "/", must_contain=['href="/"'])
check("Admin link present in nav", "/", must_contain=['href="/admin"'])

# ── SUMMARY ───────────────────────────────────────────────────
total = PASS_COUNT + FAIL_COUNT
print()
print("=" * 60)
print(f"   RESULT: {PASS_COUNT}/{total} tests passed  |  {FAIL_COUNT} failed")
print("=" * 60)
if FAIL_COUNT == 0:
    print("   ALL TESTS PASSED — MedGuide is working correctly!")
else:
    print("   FAILED TESTS:")
    for f in FAILURES:
        print(f"   {f}")
print()

sys.exit(0 if FAIL_COUNT == 0 else 1)
