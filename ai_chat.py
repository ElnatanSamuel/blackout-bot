import json
import urllib.request
import urllib.error
import time
import random
from config import GEMINI_API_KEY, ROLE_DEFINITIONS

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"

SUSPICION_LEVELS = {
    'TRUSTED': (-999, -3),
    'LEANING_CLEAN': (-3, -1),
    'UNKNOWN': (-1, 1),
    'SUSPICIOUS': (1, 4),
    'HIGH_SUSPICION': (4, 999),
}

SUSPICION_LABELS = {
    'TRUSTED': 'Trusted',
    'LEANING_CLEAN': 'Leaning Clean',
    'UNKNOWN': 'Unknown',
    'SUSPICIOUS': 'Suspicious',
    'HIGH_SUSPICION': 'Highly Suspicious',
}


def get_suspicion_level(score):
    for level, (low, high) in SUSPICION_LEVELS.items():
        if low <= score < high:
            return level
    return 'UNKNOWN'


def get_suspicion_label(score):
    return SUSPICION_LABELS[get_suspicion_level(score)]


def _get_game_event_log(game_state):
    lines = []
    if hasattr(game_state, 'vote_history') and game_state.vote_history:
        for v in game_state.vote_history:
            voter = game_state.get_player_name(v.get('voter', 0))
            target = game_state.get_player_name(v.get('target', 0)) if v.get('target') != 'skip' else 'skip'
            lines.append(f"- Round {v.get('round', '?')}: {voter} voted {target}")

    if hasattr(game_state, 'exiled_players') and game_state.exiled_players:
        for uid, data in game_state.exiled_players:
            name = game_state.get_player_name(uid)
            role = data.get('role', '?')
            lines.append(f"- {name} was exiled (was {role})")

    if hasattr(game_state, 'last_night_deaths') and game_state.last_night_deaths:
        for uid in game_state.last_night_deaths:
            name = game_state.get_player_name(uid)
            lines.append(f"- {name} died last night")

    if hasattr(game_state, 'announced_abilities') and game_state.announced_abilities:
        for ann in game_state.announced_abilities:
            lines.append(f"- Announcement: {ann}")

    return '\n'.join(lines) if lines else 'No notable events yet.'


def _get_my_action_history(game_state, bot_uid):
    lines = []
    if hasattr(game_state, 'vote_history'):
        for v in game_state.vote_history:
            if v.get('voter') == bot_uid:
                target = game_state.get_player_name(v.get('target', 0)) if v.get('target') != 'skip' else 'skip'
                lines.append(f"Round {v.get('round', '?')}: I voted {target}")

    scan_hist = game_state.scan_history.get(bot_uid, []) if hasattr(game_state, 'scan_history') else []
    for target_uid in scan_hist:
        pname = game_state.get_player_name(target_uid)
        result = game_state.scan_results.get(str(bot_uid), {}).get(str(target_uid), '?') if hasattr(game_state, 'scan_results') else '?'
        lines.append(f"I scanned {pname} = {result}")

    prot_hist = game_state.protection_history.get(bot_uid, []) if hasattr(game_state, 'protection_history') else []
    for target_uid in prot_hist[-3:]:
        pname = game_state.get_player_name(target_uid)
        lines.append(f"I protected {pname}")

    block_hist = game_state.block_history.get(bot_uid, []) if hasattr(game_state, 'block_history') else []
    for target_uid in block_hist[-3:]:
        pname = game_state.get_player_name(target_uid)
        lines.append(f"I blocked {pname}")

    return '\n'.join(lines) if lines else 'No actions recorded yet.'


def _build_chat_prompt(bot_data, game_state, player_message, extra_context=""):
    role = bot_data.get('role', 'Unknown')
    name = bot_data.get('name', 'Bot')
    personality = bot_data.get('personality', 'Quiet')
    team = ROLE_DEFINITIONS.get(role, {}).get('team', 'SURVIVOR')
    ability = ROLE_DEFINITIONS.get(role, {}).get('ability', 'None')
    limitation = ROLE_DEFINITIONS.get(role, {}).get('limitation', '')

    all_alive = game_state.get_alive_players()
    alive_names = [game_state.get_player_name(uid) for uid, _ in all_alive]
    alive_text = ', '.join(alive_names) if alive_names else 'nobody'

    dead_with_roles = []
    for uid, data in game_state.players.items():
        if not data.get('is_alive', True) and data.get('role'):
            dead_with_roles.append(f"{game_state.get_player_name(uid)} ({data['role']})")
    for uid, data in game_state.bots.items():
        if not data.get('is_alive', True) and data.get('role'):
            dead_with_roles.append(f"{game_state.get_player_name(uid)} ({data['role']})")
    dead_text = ', '.join(dead_with_roles) if dead_with_roles else 'none yet'

    events = getattr(game_state, 'last_night_deaths', [])
    deaths = ', '.join(f"{game_state.get_player_name(uid)} ({game_state.players.get(uid, game_state.bots.get(uid, {})).get('role', '?')})" for uid in events) if events else 'none'

    brain = game_state.bot_brain.get(str(bot_data.get('bot_uid', '')), {})
    suspicions = brain.get('suspicion', {})
    known_roles = brain.get('known_roles', {})

    sus_lines = []
    for uid, score in sorted(suspicions.items(), key=lambda x: x[1], reverse=True):
        pname = game_state.get_player_name(uid)
        label = get_suspicion_label(score)
        role_hint = ''
        if uid in known_roles:
            role_hint = f" [KNOWN: {known_roles[uid]}]"
        sus_lines.append(f"{pname}: {label} ({score:.1f}){role_hint}")
    sus_text = '\n'.join(f"  - {l}" for l in sus_lines[:5]) if sus_lines else '  No reads yet'

    scan_info = ""
    if hasattr(game_state, 'scan_results'):
        my_scans = game_state.scan_results.get(str(bot_data.get('bot_uid', '')), {})
        if my_scans:
            scan_parts = [f"{game_state.get_player_name(int(uid))}={res}" for uid, res in my_scans.items()]
            scan_info = f"My scan results: {', '.join(scan_parts)}."

    teammates = []
    if team == 'CORRUPT':
        for uid, data in all_alive:
            if data.get('role') in ['Blackout', 'Razor', 'Phantom', 'Thug'] and uid != bot_data.get('bot_uid', ''):
                teammates.append(f"{game_state.get_player_name(uid)} ({data['role']})")
    teammate_text = ', '.join(teammates) if teammates else 'none alive'

    if team == 'NEUTRAL':
        neutral_peers = []
        for uid, data in all_alive:
            if data.get('role') in ['Virus', 'Wraith', 'Glitch', 'Plague'] and uid != bot_data.get('bot_uid', ''):
                neutral_peers.append(f"{game_state.get_player_name(uid)} ({data['role']})")
        teammate_text = ', '.join(neutral_peers) if neutral_peers else 'none (I play solo)'

    exiled = getattr(game_state, 'exiled_players', [])
    exiled_text = ', '.join(f"{game_state.get_player_name(uid)} ({data.get('role', '?')})" for uid, data in exiled) if exiled else 'none'

    round_text = f"Round {game_state.current_round}" if game_state.current_round > 0 else "Pre-game"

    event_log = _get_game_event_log(game_state)
    my_history = _get_my_action_history(game_state, bot_data.get('bot_uid', ''))

    total_alive = len(all_alive)
    alive_corrupt_count = len([d for _, d in all_alive if d.get('role') in ['Blackout', 'Razor', 'Phantom', 'Thug']])

    prompt = f"""You are {name}, a {role} ({team} team) in a social deduction game called Blackout.
Your personality type: {personality}.
Your role ability: {ability}. Limitation: {limitation}.

GAME STATE - {round_text}:
Alive ({total_alive}): {alive_text}
Dead: {dead_text}
Last night deaths: {deaths}
Exiled so far: {exiled_text}

YOUR KNOWLEDGE:
My reads on players:
{sus_text}
{scan_info}
Teammates I know: {teammate_text}
{my_history}

EVENT LOG:
{event_log}

Someone in chat says: "{player_message}"
{extra_context}

RULES FOR YOUR RESPONSE:
- Reference SPECIFIC things that happened. Example: "After {player} got scanned SUSPICIOUS..." or "{player} voted for {target} last round, that's weird..."
- If you have scans, USE THEM. "I scanned {player} and they're clean, so..."
- If you saw voting patterns, mention them. "{player} and {player2} keep voting together..."
- If someone died and you suspected them, say "I knew {player} was off..."
- React to deaths with actual game knowledge, not generic "oh no" stuff.
- If you're corrupt, subtly push blame toward innocent players while defending your teammates.
- If you're neutral, protect your own win condition. Be sneaky.
- If you're survivor, use logic. Reference your scans and reads.
- Be conversational. React to what was JUST said. Don't lecture.
- 1-2 sentences max. No robotic disclaimers.
- NEVER say "as a [role]" or break character. You ARE that person playing the game.
"""
    return prompt


def _call_gemini(prompt, retries=2, timeout=8):
    if not GEMINI_API_KEY:
        return None

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 100,
            "temperature": 0.9,
            "topP": 0.95,
        }
    }).encode()

    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

    last_error = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            cleaned = text.strip().strip('"').strip("'")
            if cleaned and len(cleaned) > 5:
                return cleaned
            return None
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}"
            if e.code == 429:
                time.sleep(1 + attempt)
            elif e.code == 403:
                print(f"Gemini auth error (key invalid?): {e.code}")
                return None
            elif e.code >= 500:
                time.sleep(0.5)
            else:
                return None
        except urllib.error.URLError as e:
            last_error = str(e)
            time.sleep(0.3)
        except Exception as e:
            last_error = str(e)
            if attempt < retries - 1:
                time.sleep(0.3)

    print(f"Gemini failed after {retries} attempts: {last_error}")
    return None


def get_bot_response(bot_data, game_state, player_message):
    if not GEMINI_API_KEY:
        return None

    extra_context = ""
    intent = _detect_intent(player_message)
    mentioned = _find_mentioned_name(player_message, game_state)

    if intent == 'accuse' and mentioned:
        brain = game_state.bot_brain.get(str(bot_data.get('bot_uid', '')), {})
        sus = brain.get('suspicion', {})
        mentioned_uid = _find_mentioned_uid(player_message, game_state)
        my_read = sus.get(mentioned_uid, 0) if mentioned_uid else 0
        if my_read > 2:
            extra_context = f"{mentioned} is someone I also suspect (score {my_read:.1f}). I should pile on."
        elif my_read < -1:
            extra_context = f"{mentioned} is someone I trust (score {my_read:.1f}). I should defend them."
        else:
            extra_context = f"I don't have a strong read on {mentioned} yet. Need to weigh the evidence."

    elif intent == 'defend' and mentioned:
        brain = game_state.bot_brain.get(str(bot_data.get('bot_uid', '')), {})
        sus = brain.get('suspicion', {})
        mentioned_uid = _find_mentioned_uid(player_message, game_state)
        my_read = sus.get(mentioned_uid, 0) if mentioned_uid else 0
        if my_read > 2:
            extra_context = f"I actually suspect {mentioned} despite this defense (score {my_read:.1f})."
        elif my_read < -1:
            extra_context = f"I agree, {mentioned} is clean in my book (score {my_read:.1f})."
        else:
            extra_context = f"I'm not sure about {mentioned} yet."

    elif intent == 'claim':
        extra_context = f"Someone is role claiming. I need to evaluate if this is real or a fake claim."

    elif mentioned:
        extra_context = f"{mentioned} was mentioned. What do I know about them?"

    prompt = _build_chat_prompt(bot_data, game_state, player_message, extra_context)
    return _call_gemini(prompt)


def _detect_intent(text):
    t = text.lower()
    accuse_words = ['sus', 'corrupt', 'guilty', 'kill', 'vote out', 'exile', 'lying', 'liar', 'scum', 'evil', 'suspicious', 'bandwagon', 'out them']
    defend_words = ['trust', 'clean', 'innocent', 'clear', 'safe', 'believe', 'trustworthy', 'vouch', 'good person', 'town', 'helping']
    claim_words = ['i am', "i'm the", 'i claim', 'my role', 'i scan', 'i protect', 'i block', "i'm grid", "i'm volt", "i'm sheriff"]
    if any(w in t for w in accuse_words):
        return 'accuse'
    if any(w in t for w in defend_words):
        return 'defend'
    if any(w in t for w in claim_words):
        return 'claim'
    return 'neutral'


def _find_mentioned_uid(text, game_state):
    t = text.lower()
    for uid, data in game_state.get_alive_players():
        name = data.get('name', '').lower()
        if name and name in t:
            return uid
    return None


def _find_mentioned_name(text, game_state):
    t = text.lower()
    for uid, data in game_state.get_alive_players():
        name = data.get('name', '').lower()
        if name and name in t:
            return data.get('name')
    return None
