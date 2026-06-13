import json
import urllib.request
from config import GEMINI_API_KEY

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"


def _build_prompt(bot_data, game_state, player_message):
    role = bot_data.get('role', 'Unknown')
    name = bot_data.get('name', 'Bot')
    all_alive = game_state.get_alive_players()
    alive_names = ', '.join(game_state.get_player_name(uid) for uid, _ in all_alive)
    events = getattr(game_state, 'last_night_deaths', [])
    deaths = ', '.join(game_state.get_player_name(uid) for uid in events) if events else 'none'

    return (
        f"Game round {game_state.current_round}. Alive: {alive_names}. "
        f"{name} is {role}. Last night deaths: {deaths}. "
        f"Player says: \"{player_message}\". "
        f"Reply as {name} in 1 short sentence. Be concise."
    )


def _call_gemini(prompt):
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 60, "temperature": 0.8}
    }).encode()
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return text.strip()


def get_bot_response(bot_data, game_state, player_message):
    if not GEMINI_API_KEY:
        return None
    try:
        prompt = _build_prompt(bot_data, game_state, player_message)
        return _call_gemini(prompt)
    except Exception as e:
        print(f"Gemini error: {e}")
        return None
