"""
Dlhodobý integračný test — posiela request každú minútu a kontroluje odpoveď.
Spustenie: python tests/long_run_test.py
Zastavenie: Ctrl+C (vypíše súhrn a uloží report)
"""

import json
import time
import urllib.request
import urllib.error

URL = "http://pico.local/api/temperature"
INTERVAL_S = 60
REQUEST_TIMEOUT_S = 10
DURATION_S = 8 * 3600  # 8 hodín
REPORT_DIR = "."        # adresár kde sa uloží report


def _timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _check_response(raw_body):
    """Vráti (ok, chyba) pre telo odpovede."""
    try:
        data = json.loads(raw_body)
    except ValueError:
        return False, f"Neplatný JSON: {raw_body[:80]}"

    for field in ("temperature", "humidity", "unit"):
        if field not in data:
            return False, f"Chýba pole '{field}'"

    if data["unit"] != "celsius":
        return False, f"Neočakávaná jednotka: {data['unit']}"

    temp = data["temperature"]
    hum = data["humidity"]

    if temp is not None and not (-40 <= temp <= 80):
        return False, f"Teplota mimo rozsah: {temp}"
    if hum is not None and not (0 <= hum <= 100):
        return False, f"Vlhkosť mimo rozsah: {hum}"

    return True, None


def _send_request():
    """Vráti (status_code, body) alebo vyhodí výnimku."""
    req = urllib.request.Request(URL)
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
        return resp.status, resp.read().decode()


def _write_report(path, start_ts, end_ts, elapsed, ok_count, fail_count, failures):
    total = ok_count + fail_count
    success_pct = f"{ok_count / total * 100:.1f} %" if total > 0 else "N/A"
    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60

    lines = [
        "=" * 50,
        "  Integračný test — pico-env-station",
        "=" * 50,
        f"  URL:        {URL}",
        f"  Interval:   {INTERVAL_S}s",
        f"  Štart:      {start_ts}",
        f"  Koniec:     {end_ts}",
        f"  Čas behu:   {h}h {m}m {s}s",
        "-" * 50,
        f"  Requestov:  {total}",
        f"  OK:         {ok_count}",
        f"  Chýb:       {fail_count}",
        f"  Úspešnosť:  {success_pct}",
        "=" * 50,
    ]

    if failures:
        lines.append(f"\n  Zlyhania ({len(failures)}):")
        lines.append("-" * 50)
        for ts, msg in failures:
            lines.append(f"  [{ts}] {msg}")

    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ok_count = 0
    fail_count = 0
    failures = []
    start_time = time.time()
    start_ts = _timestamp()

    end_time = start_time + DURATION_S
    h_total = DURATION_S // 3600

    print(f"Integračný test — {URL}")
    print(f"Trvanie: {h_total}h | Interval: {INTERVAL_S}s | Timeout requestu: {REQUEST_TIMEOUT_S}s")
    print(f"Koniec: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print("Predčasné zastavenie: Ctrl+C\n")

    try:
        while time.time() < end_time:
            ts = _timestamp()
            try:
                status, body = _send_request()

                if status != 200:
                    fail_count += 1
                    msg = f"HTTP {status}"
                    failures.append((ts, msg))
                    print(f"[{ts}] CHYBA  {msg}")
                    continue

                ok, err = _check_response(body)
                if ok:
                    ok_count += 1
                    data = json.loads(body)
                    print(f"[{ts}] OK     {data['temperature']} °C  {data['humidity']} %")
                else:
                    fail_count += 1
                    msg = f"Telo: {err}"
                    failures.append((ts, msg))
                    print(f"[{ts}] CHYBA  {msg}")

            except urllib.error.URLError as e:
                fail_count += 1
                msg = f"Spojenie: {e.reason}"
                failures.append((ts, msg))
                print(f"[{ts}] CHYBA  {msg}")
            except TimeoutError:
                fail_count += 1
                msg = f"Timeout po {REQUEST_TIMEOUT_S}s"
                failures.append((ts, msg))
                print(f"[{ts}] CHYBA  {msg}")
            except Exception as e:
                fail_count += 1
                msg = f"{type(e).__name__}: {e}"
                failures.append((ts, msg))
                print(f"[{ts}] CHYBA  {msg}")

            remaining = end_time - time.time()
            time.sleep(min(INTERVAL_S, max(0, remaining)))

    except KeyboardInterrupt:
        print("\n(prerušené používateľom)")

    end_ts = _timestamp()
    elapsed = int(time.time() - start_time)
    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
    total = ok_count + fail_count

    print(f"\n--- Súhrn ---")
    print(f"Čas behu:  {h}h {m}m {s}s")
    print(f"Requestov: {total}")
    print(f"OK:        {ok_count}")
    print(f"Chýb:      {fail_count}")
    if total > 0:
        print(f"Úspešnosť: {ok_count / total * 100:.1f} %")

    report_name = f"long_run_report_{start_ts.replace(':', '-').replace(' ', '_')}.txt"
    report_path = f"{REPORT_DIR}/{report_name}"
    _write_report(report_path, start_ts, end_ts, elapsed, ok_count, fail_count, failures)
    print(f"\nReport uložený: {report_path}")


if __name__ == "__main__":
    main()
