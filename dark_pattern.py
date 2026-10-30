"""
ApplyCopilot Protocol 05: Anti-Dark-Pattern Fee Stripper Engine
Autonomously audits checkout DOM trees, strips sneaky pre-checked fees,
and saves user money on travel & ticketing portals.
"""

import os
import re
import sys
import time

# Ensure UTF-8 output on Windows console
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

DARK_PATTERN_KEYWORDS = [
    r"insur(ance)?",
    r"protect(ion)?",
    r"donat(e|ion)",
    r"charit(y|able)",
    r"priority\s+baggage",
    r"fast\s+check-?in",
    r"care\s+plan",
    r"cancellation\s+protect",
    r"handling\s+fee"
]

def strip_dark_patterns(page):
    """
    Scans the currently loaded page for deceptive checked checkboxes and unchecks them.
    Returns audit telemetry: items stripped, fees saved, original vs cleaned total.
    """
    print("\n[ANTI-DARK-PATTERN] Initiating DOM scan for deceptive add-ons...")
    
    # 1. Grab initial total if present
    initial_total_text = ""
    for sel in ["#total-fare", ".total-amount", ".grand-total", "span:has-text('Total')"]:
        try:
            elem = page.locator(sel).first
            if elem.is_visible():
                initial_total_text = elem.inner_text().strip()
                break
        except Exception:
            pass

    # 2. Find all checkboxes and inspect their checked status statically
    all_boxes = page.locator('input[type="checkbox"]').all()
    print(f"[ANTI-DARK-PATTERN] Found {len(all_boxes)} total checkboxes on page.")
    
    stripped_items = []
    
    for box in all_boxes:
        try:
            if not box.is_checked():
                continue
                
            # Check parent label or surrounding text for deceptive keywords
            parent_text = box.evaluate("el => (el.closest('label') || el.closest('div') || el.parentElement).innerText")
            
            # Match against dark pattern regex patterns
            matched_pattern = None
            for pat in DARK_PATTERN_KEYWORDS:
                if re.search(pat, parent_text, re.IGNORECASE):
                    matched_pattern = pat
                    break
            
            if matched_pattern:
                clean_title = parent_text.split('\n')[0].strip()
                print(f"  [!] DECEPTIVE ADD-ON DETECTED: '{clean_title}' (Matched: {matched_pattern})")
                
                # Programmatically uncheck
                box.uncheck()
                stripped_items.append(clean_title)
                page.wait_for_timeout(100) # allow JS handlers to fire
        except Exception as e:
            print(f"  [?] Error inspecting checkbox: {e}")

    # 3. Read updated total
    cleaned_total_text = ""
    for sel in ["#total-fare", ".total-amount", ".grand-total", "span:has-text('Total')"]:
        try:
            elem = page.locator(sel).first
            if elem.is_visible():
                cleaned_total_text = elem.inner_text().strip()
                break
        except Exception:
            pass

    return {
        "status": "SANITIZED",
        "dark_patterns_found": len(stripped_items),
        "items_stripped": stripped_items,
        "initial_total": initial_total_text,
        "cleaned_total": cleaned_total_text,
        "clean_checkout_ready": True
    }


def run_demo(mock_html_path="mock_checkout.html", headless=True):
    if mock_html_path.startswith("http"):
        file_url = mock_html_path
    else:
        abs_path = os.path.abspath(mock_html_path)
        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
    
    print(f"=== TESTING PROTOCOL 05: ANTI-DARK-PATTERN STRIPPER ===")
    print(f"Target Checkout Page: {file_url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(file_url)
        page.wait_for_load_state("domcontentloaded")
        
        telemetry = strip_dark_patterns(page)
        
        # Take verification screenshot
        screenshot_path = "cleaned_checkout_proof.png"
        page.screenshot(path=screenshot_path)
        print(f"\n[OK] Verification screenshot captured: {screenshot_path}")
        browser.close()
        
    print("\n--- SANITIZATION TELEMETRY ---")
    print(f"  * Status: {telemetry['status']}")
    print(f"  * Deceptive Patterns Stripped: {telemetry['dark_patterns_found']}")
    for idx, item in enumerate(telemetry['items_stripped'], 1):
        print(f"    {idx}. {item}")
    print(f"  * Before Jarvis: {telemetry['initial_total']}")
    print(f"  * After Jarvis:  {telemetry['cleaned_total']}")
    return telemetry


if __name__ == "__main__":
    run_demo(headless=True)
