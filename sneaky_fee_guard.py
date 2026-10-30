"""
ApplyCopilot Sneaky Fee & Drip-Pricing Interceptor (Voice Financial Anchor).
Audits checkout totals against the voice-approved amount and strips hidden fees.
"""

import re

DARK_PATTERN_KEYWORDS = [
    r"insur(ance)?",
    r"protect(ion)?",
    r"donat(e|ion)",
    r"charit(y|able)",
    r"priority\s+baggage",
    r"fast\s+check-?in",
    r"care\s+plan",
    r"cancellation\s+protect",
    r"handling\s+fee",
    r"convenience\s+fee",
    r"platform\s+fee",
    r"service\s+surcharge",
    r"carbon\s+offset"
]

def extract_voice_approved_amount(user_prompt):
    """
    Parses currency amounts from user voice or text instructions:
    e.g. 'pay ₹4,650', 'book for 4200', 'budget 4650', 'under 5000 rupees', 'pay $50'.
    """
    if not user_prompt:
        return None, None

    # Match INR (₹ or Rs or INR)
    inr_match = re.search(r'(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)', user_prompt, re.IGNORECASE)
    if inr_match:
        val = float(inr_match.group(1).replace(',', ''))
        return val, "INR"

    # Match USD ($ or USD)
    usd_match = re.search(r'(?:\$|usd)\s*([\d,]+(?:\.\d+)?)', user_prompt, re.IGNORECASE)
    if usd_match:
        val = float(usd_match.group(1).replace(',', ''))
        return val, "USD"

    # Match generic number after 'for', 'amount', 'pay', 'budget', 'under'
    num_match = re.search(r'(?:pay|amount|for|budget|under|total)\s*(?:of\s*)?([\d,]+(?:\.\d+)?)', user_prompt, re.IGNORECASE)
    if num_match:
        val = float(num_match.group(1).replace(',', ''))
        return val, "INR"

    return None, None


async def audit_and_strip_checkout(page, voice_approved_amount=None):
    """
    Scans the checkout DOM for deceptive pre-checked items and verifies if the final
    total matches what the user approved by voice.
    """
    telemetry = {
        "status": "CLEAN",
        "voice_approved": voice_approved_amount,
        "initial_total": 0.0,
        "final_total": 0.0,
        "currency": "INR",
        "stripped_items": [],
        "quiet_added_fee": 0.0,
        "quiet_fee_details": "",
        "action_required": "PROCEED"  # 'PROCEED' or 'INTERCEPT_VOICE_MISMATCH'
    }

    if not page:
        return telemetry

    # 1. Read initial total from page
    initial_total_str = await _extract_total_text(page)
    initial_val = _parse_number(initial_total_str)
    telemetry["initial_total"] = initial_val

    # 2. Scan and uncheck deceptive pre-checked add-ons
    stripped = []
    try:
        checkboxes = await page.locator('input[type="checkbox"]').all()
        for box in checkboxes:
            try:
                is_checked = await box.is_checked()
                if not is_checked:
                    continue

                parent_text = await box.evaluate("el => (el.closest('label') || el.closest('div') || el.parentElement).innerText")
                for pat in DARK_PATTERN_KEYWORDS:
                    if re.search(pat, parent_text, re.IGNORECASE):
                        clean_title = parent_text.split('\n')[0].strip()
                        print(f"[SNEAKY FEE GUARD] Stripping unapproved pre-checked fee: '{clean_title}'")
                        await box.uncheck()
                        stripped.append(clean_title)
                        await page.wait_for_timeout(150)
                        break
            except Exception:
                pass
    except Exception as e:
        print(f"[!] Checkbox scan error: {e}")

    telemetry["stripped_items"] = stripped

    # 3. Read updated final total after stripping
    final_total_str = await _extract_total_text(page)
    final_val = _parse_number(final_total_str)
    if final_val == 0.0 and initial_val > 0.0 and len(stripped) == 0:
        final_val = initial_val
    telemetry["final_total"] = final_val

    # 4. Check for Quiet/Drip Fees that user never approved by voice
    if voice_approved_amount and voice_approved_amount > 0:
        if final_val > (voice_approved_amount + 1.0):  # Allow tiny rounding margin
            excess = final_val - voice_approved_amount
            telemetry["status"] = "UNAPPROVED_FEE_DETECTED"
            telemetry["quiet_added_fee"] = excess
            telemetry["action_required"] = "INTERCEPT_VOICE_MISMATCH"
            
            # Inspect DOM to identify the sneakily added fee label
            quiet_fee_desc = await _detect_quiet_fee_item(page, excess)
            telemetry["quiet_fee_details"] = quiet_fee_desc
            print(f"[GUARDRAIL ALERT] Quiet fee detected! Voice approved: {voice_approved_amount}, Screen: {final_val}, Excess: +{excess} ({quiet_fee_desc})")
        else:
            if stripped:
                telemetry["status"] = "STRIPPED_AND_MATCHED"
            else:
                telemetry["status"] = "MATCHED_VOICE_APPROVAL"
    else:
        if stripped:
            telemetry["status"] = "STRIPPED_FEES"

    return telemetry


async def _extract_total_text(page):
    selectors = [
        "#total-fare",
        ".total-amount",
        ".grand-total",
        "#grand-total",
        "#final-amount",
        ".final-price",
        "span:has-text('Total Amount')",
        "span:has-text('Total')"
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if await loc.is_visible():
                txt = await loc.inner_text()
                if any(c.isdigit() for c in txt):
                    return txt.strip()
        except Exception:
            pass
    return ""


def _parse_number(text):
    if not text:
        return 0.0
    match = re.search(r'[\d,]+(?:\.\d+)?', text)
    if match:
        try:
            return float(match.group(0).replace(',', ''))
        except ValueError:
            return 0.0
    return 0.0


async def _detect_quiet_fee_item(page, excess):
    """Inspects the page breakdown to name the quietly added fee."""
    try:
        script = """
        (() => {
            const items = [];
            document.querySelectorAll('.item-row, .fee-row, .breakdown-item, tr, div').forEach(el => {
                const txt = el.innerText || '';
                if (txt.includes('Fee') || txt.includes('Tax') || txt.includes('Charge') || txt.includes('Surcharge') || txt.includes('Convenience') || txt.includes('Platform')) {
                    if (txt.length < 120) items.push(txt.replace(/\\s+/g, ' ').trim());
                }
            });
            return items.slice(0, 5);
        })()
        """
        fee_candidates = await page.evaluate(script)
        if fee_candidates:
            return fee_candidates[0]
    except Exception:
        pass
    return f"Unapproved Surcharge / Quiet Convenience Fee (+₹{excess:,.0f})"
