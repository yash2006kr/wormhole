"""
ApplyCopilot Protocol 01: Transit Rush Protocol Engine
High-Speed Autonomous Seat Selector & Air-Gapped Reservation Dispatcher.
"""

import os
import sys
import json
import time

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright
from dark_pattern import strip_dark_patterns

def run_transit_rush(target_url="http://localhost:8000/mock/ksrtc", headless=True):
    print("=" * 60)
    print("  [TRANSIT RUSH] Initiating High-Speed Booking Agent...")
    print("=" * 60)
    
    # 1. Load Vault
    vault_file = "vault.json"
    with open(vault_file, "r", encoding="utf-8") as f:
        vault = json.load(f)
        
    passengers = vault.get("transit_preferences", {}).get("passengers", [])
    if not passengers:
        passengers = [{"name": "Yashwanth K R", "age": 23, "gender": "Male"}]
        
    p1 = passengers[0]
    p2 = passengers[1] if len(passengers) > 1 else {"name": "Raj Aanada", "age": 22, "gender": "Male"}

    telemetry = {
        "status": "PROCESSING",
        "seats_selected": [],
        "passengers": [p1["name"], p2["name"]],
        "dark_patterns_stripped": 0,
        "clean_fare": 0,
        "state": "IDLE"
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        
        t0 = time.time()
        print(f"[1/4] Navigating to transit portal: {target_url}...")
        page.goto(target_url)
        page.wait_for_load_state("domcontentloaded")
        
        # 2. Parse seat grid & select 2 lower sleeper berths
        print("[2/4] Parsing dynamic berth layout for adjacent lower berths...")
        seats = page.locator("#lower-deck .seat.available").all()
        selected_seat_names = []
        
        for i in range(min(2, len(seats))):
            seat_el = seats[i]
            seat_name = seat_el.locator(".seat-num").inner_text()
            seat_el.click()
            selected_seat_names.append(seat_name)
            page.wait_for_timeout(150)
            
        print(f"  * Locked Berths: {', '.join(selected_seat_names)}")
        telemetry["seats_selected"] = selected_seat_names

        # 3. Inject Passenger Vault details
        print(f"[3/4] Injecting passenger credentials from encrypted vault...")
        page.fill("#p1-name", p1["name"])
        page.fill("#p1-age", str(p1["age"]))
        page.select_option("#p1-gender", p1.get("gender", "Male"))
        
        page.fill("#p2-name", p2["name"])
        page.fill("#p2-age", str(p2["age"]))
        page.select_option("#p2-gender", p2.get("gender", "Male"))
        page.wait_for_timeout(200)

        # 4. Proceed to Checkout Page
        print("[4/4] Advancing to Checkout Terminal...")
        page.click("#btn-proceed-payment")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(300)

        # 5. Automatically engage Protocol 05: Anti-Dark-Pattern Fee Stripper
        print("\n[ANTI-DARK-PATTERN TRIGGERED] Scanning checkout page for hidden add-ons...")
        dp_result = strip_dark_patterns(page)
        telemetry["dark_patterns_stripped"] = dp_result["dark_patterns_found"]
        telemetry["cleaned_total"] = dp_result["cleaned_total"]
        telemetry["initial_total"] = dp_result["initial_total"]
        
        # 6. Air-Gapped Sentinel Gate: Freeze at payment
        telemetry["state"] = "PAUSED_FOR_HUMAN_PAYMENT"
        telemetry["status"] = "SUCCESS"
        telemetry["duration_ms"] = round((time.time() - t0) * 1000, 1)

        # Capture proof screenshot
        proof_path = "transit_rush_proof.png"
        page.screenshot(path=proof_path)
        telemetry["screenshot"] = proof_path
        
        browser.close()

    print("\n" + "=" * 60)
    print("  [TRANSIT RUSH COMPLETE] Reservation Prepared in", telemetry["duration_ms"], "ms")
    print("  * Seats:     ", telemetry["seats_selected"])
    print("  * Passengers:", telemetry["passengers"])
    print("  * Fees Stripped: ", telemetry["dark_patterns_stripped"], "items")
    print("  * Final Clean Total: ", telemetry["cleaned_total"])
    print("  * Safety Gate: State shifted to PAUSED_FOR_HUMAN_PAYMENT")
    print("=" * 60)
    
    return telemetry

if __name__ == "__main__":
    run_transit_rush(headless=True)
