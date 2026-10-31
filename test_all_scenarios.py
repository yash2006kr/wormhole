import asyncio
from agent_core import SemanticIntentAnalyzer, AgentCore

async def test_scenarios():
    print("=================================================================")
    print("  🧪 TESTING ALL SCENARIOS REPORTED BY USER")
    print("=================================================================\n")

    core = AgentCore()

    # Scenario 1: Food query with repetition and speech-to-text typo
    raw_prompt_1 = "best biryani best biryani in Vijayanagar affordable price and good test"
    cleaned_1 = SemanticIntentAnalyzer.clean_voice_text(raw_prompt_1)
    print(f"[TEST 1: Speech-to-Text Cleaning]")
    print(f"  Raw:     '{raw_prompt_1}'")
    print(f"  Cleaned: '{cleaned_1}'")
    assert "best biryani in Vijayanagar" in cleaned_1, "Failed to deduplicate repeated words"
    assert "good taste" in cleaned_1, "Failed to correct 'good test' -> 'good taste'"
    is_in_page_1 = SemanticIntentAnalyzer.is_in_page_control(cleaned_1, "https://suno.com/create")
    assert not is_in_page_1, "Food query should NOT be considered in-page on Suno AI"
    print("  -> Passed: Cleans typos, stutters, and correctly flags as new destination search.\n")

    # Scenario 2: Suno AI create follow-up
    print(f"[TEST 2: Suno AI Follow-up & Click Create]")
    core.session_history.append({
        "role": "user",
        "text": "make a song about a boy handsome almost near my shoulder but never talk about me add this to suno ai again"
    })
    action_suno_home = await core._decide_next_action(
        "create", "https://suno.com", "Suno", dom_elements="button: Create"
    )
    print(f"  Suno Homepage + 'create' -> Action: {action_suno_home['action']}, URL: {action_suno_home.get('url')}")
    assert action_suno_home["action"] == "navigate" and "/create" in action_suno_home["url"]

    action_suno_create = await core._decide_next_action(
        "click create", "https://suno.com/create", "Suno Studio", dom_elements="button: Create"
    )
    print(f"  Suno /create + 'click create' -> Action: {action_suno_create['action']}, Selector: {action_suno_create.get('selector')}")
    assert action_suno_create["action"] == "click" and "Create" in action_suno_create["selector"]
    print("  -> Passed: Stays in Suno AI studio and clicks Create instead of Google Searching.\n")

    # Scenario 3: YouTube Search Specific Song
    print(f"[TEST 3: YouTube Search Specific Song]")
    action_yt = await core._decide_next_action(
        "🔍 Search Specific Song", "https://www.youtube.com/watch?v=123", "YouTube Video"
    )
    print(f"  YouTube + 'Search Specific Song' -> Action: {action_yt['action']}, Options: {action_yt.get('options')}")
    assert len(action_yt.get("options", [])) > 0
    assert any("Arijit" in o or "Alan Walker" in o or "Lofi" in o for o in action_yt.get("options", []))
    print("  -> Passed: Offers instant 1-click popular song choices instead of looping greeting.\n")

    # Scenario 4: AbhiBus Route Direct Navigation
    print(f"[TEST 4: AbhiBus Route Search]")
    route = SemanticIntentAnalyzer.parse_transit_route("🚌 Bangalore to Hyderabad")
    assert route == ("Bangalore", "Hyderabad", False)
    action_abhibus = await core._decide_next_action(
        "🚌 Bangalore to Hyderabad", "https://www.abhibus.com", "AbhiBus"
    )
    print(f"  AbhiBus + '🚌 Bangalore to Hyderabad' -> Action: {action_abhibus['action']}, Route: {action_abhibus.get('origin')} -> {action_abhibus.get('dest')}")
    assert action_abhibus["action"] == "abhibus_route_search"
    print("  -> Passed: Directly triggers route search Bangalore -> Hyderabad without repeating greeting.\n")

    # Scenario 5: Google Maps / Swiggy chips
    print(f"[TEST 5: Quick Action Chips]")
    action_maps = await core._decide_next_action(
        "📍 Open in Google Maps", "https://www.google.com/search?q=biryani", "Google Search"
    )
    print(f"  Google Search + 'Open in Google Maps' -> Action: {action_maps['action']}, URL: {action_maps.get('url')}")
    assert action_maps["action"] == "navigate" and "google.com/maps" in action_maps["url"]

    action_swiggy = await core._decide_next_action(
        "🛵 Order on Swiggy", "https://www.google.com/search?q=biryani", "Google Search"
    )
    print(f"  Google Search + 'Order on Swiggy' -> Action: {action_swiggy['action']}, URL: {action_swiggy.get('url')}")
    assert action_swiggy["action"] == "navigate" and "swiggy.com" in action_swiggy["url"]
    print("  -> Passed: Action chips navigate cleanly to Google Maps and Swiggy.\n")

    print("=================================================================")
    print("  ✅ ALL 5 SCENARIOS PASSED WITH 100% SUCCESS!")
    print("=================================================================\n")

if __name__ == "__main__":
    asyncio.run(test_scenarios())
