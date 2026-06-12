import os
import time
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from threading import Thread

from config import TELEGRAM_BOT_TOKEN, GAME_SETTINGS, ROLE_POOLS, ROLE_DEFINITIONS, BOT_NAMES, BOT_PERSONALITIES, SUSPICION_WEIGHTS
from database import (
    init_db, save_player, update_player_elo, increment_player_stats,
    get_player, get_leaderboard, create_game, end_game, add_game_player,
    kill_player, get_game_players, get_alive_players, get_alive_corrupt,
    log_game_event, get_game_log, update_ai_memory, get_ai_memories,
    get_player_game_history
)
from game_messages import (
    START_TALE, ROLE_BRIEFINGS, DAWN_MESSAGES, NIGHT_MESSAGES,
    WIN_MESSAGES, LOBBY_MESSAGES, HELP_MESSAGE, DEAD_SPECTATE_MESSAGE,
    VOTE_PUBLIC_MESSAGE, VOTE_SKIP_PUBLIC_MESSAGE, STATIC_PASSIVE_MESSAGE,
    RELAY_PASSIVE_MESSAGE, PING_PASSIVE_MESSAGE, BOT_CHAT_TEMPLATES,
    ELO_MESSAGES, STATS_MESSAGE, LEADERBOARD_MESSAGE, LEADERBOARD_ENTRY,
    GAME_REPLAY_HEADER, GAME_REPLAY_ENTRY
)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

game_states = {}

class GameState:
    def __init__(self, chat_id, creator_id, corrupt_count):
        self.chat_id = chat_id
        self.creator_id = creator_id
        self.corrupt_count = corrupt_count
        self.game_id = None
        self.players = {}
        self.bots = {}
        self.current_phase = 'LOBBY'
        self.current_round = 0
        self.night_actions = {}
        self.votes = {}
        self.message_timestamps = {}
        self.used_abilities = {}
        self.marked_players = {}
        self.infected_players = {}
        self.protection_history = {}
        self.block_history = {}
        self.scan_history = {}
        self.virus_uses = {}
        self.wraith_uses = {}
        self.plague_infections = {}
        self.game_start_time = None
        self.auto_start_timer = None
        self.discussion_timer = None
        self.voting_timer = None

    def can_message(self, user_id):
        now = datetime.now()
        if user_id in self.message_timestamps:
            last_msg = self.message_timestamps[user_id]
            cooldown = GAME_SETTINGS['BOT_SPAM_COOLDOWN'] if self.is_ai(user_id) else GAME_SETTINGS['ANTI_SPAM_COOLDOWN']
            if (now - last_msg).total_seconds() < cooldown:
                return False
        self.message_timestamps[user_id] = now
        return True

    def is_ai(self, user_id):
        return user_id in self.bots

    def get_player_name(self, user_id):
        if user_id in self.players:
            return self.players[user_id].get('name', f'User_{user_id}')
        elif user_id in self.bots:
            return self.bots[user_id].get('name', f'Bot_{user_id}')
        return f'Unknown_{user_id}'

    def get_alive_players(self):
        alive = []
        for uid, data in self.players.items():
            if data.get('is_alive', True):
                alive.append((uid, data))
        for uid, data in self.bots.items():
            if data.get('is_alive', True):
                alive.append((uid, data))
        return alive

    def get_alive_corrupt(self):
        corrupt = []
        for uid, data in self.players.items():
            if data.get('is_alive', True) and data.get('role') in ['Blackout', 'Razor', 'Phantom', 'Thug']:
                corrupt.append((uid, data))
        for uid, data in self.bots.items():
            if data.get('is_alive', True) and data.get('role') in ['Blackout', 'Razor', 'Phantom', 'Thug']:
                corrupt.append((uid, data))
        return corrupt

    def get_alive_survivors(self):
        survivors = []
        for uid, data in self.players.items():
            if data.get('is_alive', True) and data.get('role') in ROLE_POOLS['SURVIVOR_ABILITY'] + ROLE_POOLS['SURVIVOR_VANILLA']:
                survivors.append((uid, data))
        for uid, data in self.bots.items():
            if data.get('is_alive', True) and data.get('role') in ROLE_POOLS['SURVIVOR_ABILITY'] + ROLE_POOLS['SURVIVOR_VANILLA']:
                survivors.append((uid, data))
        return survivors

    def get_alive_neutrals(self):
        neutrals = []
        for uid, data in self.players.items():
            if data.get('is_alive', True) and data.get('role') in ROLE_POOLS['NEUTRAL']:
                neutrals.append((uid, data))
        for uid, data in self.bots.items():
            if data.get('is_alive', True) and data.get('role') in ROLE_POOLS['NEUTRAL']:
                neutrals.append((uid, data))
        return neutrals

    def check_win_condition(self):
        alive_corrupt = self.get_alive_corrupt()
        alive_survivors = self.get_alive_survivors()
        alive_neutrals = self.get_alive_neutrals()
        all_alive = self.get_alive_players()

        if len(alive_survivors) == 0 and len(alive_neutrals) == 0:
            return 'CORRUPT', None

        if len(alive_corrupt) == 0 and len(alive_neutrals) == 0:
            return 'SURVIVOR', None

        for uid, data in alive_neutrals:
            if data['role'] == 'Wraith' and len(all_alive) == 1:
                return 'NEUTRAL', uid

        return None, None

def assign_roles(game_state):
    all_uids = list(game_state.players.keys()) + list(game_state.bots.keys())
    random.shuffle(all_uids)

    corrupt_roles = []
    if game_state.corrupt_count == 1:
        corrupt_roles = [random.choice(['Blackout', 'Razor', 'Thug'])]
    else:
        primary = random.choice(['Blackout', 'Razor'])
        secondary = random.choice(['Thug', 'Thug'])
        corrupt_roles = [primary, secondary]

    neutral_count = random.choice([0, 1, 2])
    neutral_roles = random.sample(ROLE_POOLS['NEUTRAL'], min(neutral_count, len(ROLE_POOLS['NEUTRAL'])))

    survivor_count = 6
    vanilla_count = 2
    ability_count = survivor_count - vanilla_count

    vanilla_roles = random.choices(ROLE_POOLS['SURVIVOR_VANILLA'], k=vanilla_count)
    ability_roles = random.sample(ROLE_POOLS['SURVIVOR_ABILITY'], min(ability_count, len(ROLE_POOLS['SURVIVOR_ABILITY'])))

    all_roles = corrupt_roles + neutral_roles + ability_roles + vanilla_roles
    while len(all_roles) < len(all_uids):
        all_roles.append(random.choice(ROLE_POOLS['SURVIVOR_VANILLA']))

    random.shuffle(all_roles)

    for idx, uid in enumerate(all_uids):
        role = all_roles[idx] if idx < len(all_roles) else random.choice(ROLE_POOLS['SURVIVOR_VANILLA'])
        if uid in game_state.players:
            game_state.players[uid]['role'] = role
        elif uid in game_state.bots:
            game_state.bots[uid]['role'] = role

        save_player(uid, game_state.get_player_name(uid), game_state.is_ai(uid))
        add_game_player(game_state.game_id, uid, role)

def send_role_briefings(game_state):
    corrupt_names = []
    for uid, data in game_state.get_alive_corrupt():
        corrupt_names.append(game_state.get_player_name(uid))

    for uid, data in game_state.players.items():
        role = data.get('role')
        if not role:
            continue

        teammates = ', '.join([name for name in corrupt_names if name != game_state.get_player_name(uid)]) if role in ['Blackout', 'Razor', 'Phantom', 'Thug'] else ''

        targets = []
        if role == 'Virus':
            potential_targets = [uid2 for uid2, d2 in game_state.players.items() if uid2 != uid and d2.get('role') not in ['Blackout', 'Razor', 'Phantom', 'Thug']]
            targets = random.sample(potential_targets, min(3, len(potential_targets)))
            targets = [game_state.get_player_name(t) for t in targets]

        briefing = ROLE_BRIEFINGS.get(role, '').format(
            teammates=teammates,
            targets=', '.join(targets) if targets else ''
        )

        try:
            bot.send_message(uid, briefing, parse_mode='Markdown')
        except Exception:
            bot.send_message(game_state.chat_id,
                f"⚠️ Couldn't DM {game_state.get_player_name(uid)}. Make sure you started a PM with this bot!",
                parse_mode='Markdown')

    for uid, data in game_state.bots.items():
        role = data.get('role')
        if role in ['Blackout', 'Razor', 'Phantom', 'Thug']:
            game_state.bots[uid]['teammates'] = [uid2 for uid2, d2 in game_state.get_alive_corrupt() if uid2 != uid]

def start_night_phase(game_state):
    game_state.current_phase = 'NIGHT'
    game_state.current_round += 1
    game_state.night_actions = {}
    game_state.votes = {}

    bot.send_message(game_state.chat_id, NIGHT_MESSAGES['night_start'], parse_mode='Markdown')

    for uid, data in game_state.players.items():
        if not data.get('is_alive', True):
            continue

        role = data.get('role')
        if role in ['Blackout', 'Razor', 'Thug']:
            send_kill_prompt(game_state, uid)
        elif role == 'Phantom':
            send_mark_prompt(game_state, uid)
        elif role in ['Virus', 'Wraith']:
            send_neutral_kill_prompt(game_state, uid)
        elif role == 'Glitch':
            send_glitch_prompt(game_state, uid)
        elif role == 'Plague':
            send_plague_prompt(game_state, uid)
        elif role == 'Volt':
            send_protect_prompt(game_state, uid)
        elif role == 'Grid':
            send_scan_prompt(game_state, uid)
        elif role == 'Bunker':
            send_block_prompt(game_state, uid)
        elif role == 'Kernel':
            send_kernel_prompt(game_state, uid)
        elif role == 'Flare':
            send_flare_prompt(game_state, uid)
        elif role == 'Sheriff':
            send_sheriff_prompt(game_state, uid)

    resolve_bot_night_actions(game_state)
    schedule_dawn(game_state)

def send_kill_prompt(game_state, uid):
    markup = InlineKeyboardMarkup()
    for uid2, data2 in game_state.get_alive_players():
        if uid2 != uid:
            name = game_state.get_player_name(uid2)
            markup.add(InlineKeyboardButton(f"Kill: {name}", callback_data=f"kill_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['choose_target'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_mark_prompt(game_state, uid):
    if game_state.used_abilities.get(f"phantom_{uid}", 0) % 2 == 1:
        return

    markup = InlineKeyboardMarkup()
    for uid2, data2 in game_state.get_alive_players():
        if uid2 != uid and data2.get('role') in ROLE_POOLS['SURVIVOR_ABILITY']:
            name = game_state.get_player_name(uid2)
            markup.add(InlineKeyboardButton(f"Mark: {name}", callback_data=f"mark_{uid2}"))
    try:
        bot.send_message(uid, "Choose a player to mark:", reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_neutral_kill_prompt(game_state, uid):
    role = game_state.players.get(uid, {}).get('role') or game_state.bots.get(uid, {}).get('role')
    uses = game_state.virus_uses.get(uid, 0) if role == 'Virus' else game_state.wraith_uses.get(uid, 0)

    if uses >= 2:
        return

    markup = InlineKeyboardMarkup()
    for uid2, data2 in game_state.get_alive_players():
        if uid2 != uid:
            name = game_state.get_player_name(uid2)
            markup.add(InlineKeyboardButton(f"Kill: {name}", callback_data=f"neutral_kill_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['choose_target'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_glitch_prompt(game_state, uid):
    dead_with_abilities = []
    for uid2, data2 in game_state.players.items():
        if not data2.get('is_alive', True) and data2.get('role') in ROLE_POOLS['SURVIVOR_ABILITY']:
            dead_with_abilities.append((uid2, data2))

    if not dead_with_abilities:
        return

    markup = InlineKeyboardMarkup()
    for uid2, data2 in dead_with_abilities:
        name = game_state.get_player_name(uid2)
        markup.add(InlineKeyboardButton(f"Steal: {name} ({data2['role']})", callback_data=f"steal_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['glitch_steal'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_plague_prompt(game_state, uid):
    if game_state.plague_infections.get(uid, 0) >= 3:
        return

    markup = InlineKeyboardMarkup()
    for uid2, data2 in game_state.get_alive_players():
        if uid2 != uid:
            name = game_state.get_player_name(uid2)
            markup.add(InlineKeyboardButton(f"Infect: {name}", callback_data=f"infect_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['plague_infect'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_protect_prompt(game_state, uid):
    last_protected = game_state.protection_history.get(uid, [])
    markup = InlineKeyboardMarkup()
    for uid2, data2 in game_state.get_alive_players():
        if uid2 != uid and uid2 not in last_protected[-2:]:
            name = game_state.get_player_name(uid2)
            markup.add(InlineKeyboardButton(f"Protect: {name}", callback_data=f"protect_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['ability_prompt'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_scan_prompt(game_state, uid):
    last_scanned = game_state.scan_history.get(uid, [])
    markup = InlineKeyboardMarkup()
    for uid2, data2 in game_state.get_alive_players():
        if uid2 != uid and uid2 not in last_scanned[-2:]:
            name = game_state.get_player_name(uid2)
            markup.add(InlineKeyboardButton(f"Scan: {name}", callback_data=f"scan_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['ability_prompt'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_block_prompt(game_state, uid):
    last_blocked = game_state.block_history.get(uid, [])
    markup = InlineKeyboardMarkup()
    for uid2, data2 in game_state.get_alive_players():
        if uid2 != uid and uid2 not in last_blocked[-2:]:
            name = game_state.get_player_name(uid2)
            markup.add(InlineKeyboardButton(f"Block: {name}", callback_data=f"block_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['ability_prompt'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_kernel_prompt(game_state, uid):
    if game_state.used_abilities.get(f"kernel_{uid}", False):
        return

    markup = InlineKeyboardMarkup()
    for uid2, data2 in game_state.get_alive_players():
        if uid2 != uid:
            name = game_state.get_player_name(uid2)
            markup.add(InlineKeyboardButton(f"Reveal: {name}", callback_data=f"reveal_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['ability_prompt'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_flare_prompt(game_state, uid):
    if game_state.used_abilities.get(f"flare_{uid}", False):
        return

    dead_players = [(uid2, data2) for uid2, data2 in game_state.players.items() if not data2.get('is_alive', True)]
    if not dead_players:
        return

    markup = InlineKeyboardMarkup()
    for uid2, data2 in dead_players:
        name = game_state.get_player_name(uid2)
        markup.add(InlineKeyboardButton(f"Revive: {name}", callback_data=f"revive_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['ability_prompt'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def send_sheriff_prompt(game_state, uid):
    markup = InlineKeyboardMarkup()
    for uid2, data2 in game_state.get_alive_players():
        if uid2 != uid:
            name = game_state.get_player_name(uid2)
            markup.add(InlineKeyboardButton(f"Execute: {name}", callback_data=f"sheriff_{uid2}"))
    try:
        bot.send_message(uid, NIGHT_MESSAGES['choose_target'], reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass

def resolve_bot_night_actions(game_state):
    for uid, data in game_state.bots.items():
        if not data.get('is_alive', True):
            continue

        role = data.get('role')
        alive_players = game_state.get_alive_players()
        alive_targets = [(uid2, d2) for uid2, d2 in alive_players if uid2 != uid]

        if not alive_targets:
            continue

        if role in ['Blackout', 'Razor', 'Thug']:
            target = choose_bot_kill_target(game_state, uid, alive_targets)
            game_state.night_actions[f"kill_{uid}"] = target

        elif role == 'Phantom':
            if game_state.used_abilities.get(f"phantom_{uid}", 0) % 2 == 0:
                ability_targets = [(uid2, d2) for uid2, d2 in alive_targets if d2.get('role') in ROLE_POOLS['SURVIVOR_ABILITY']]
                if ability_targets:
                    target = random.choice(ability_targets)[0]
                    game_state.night_actions[f"mark_{uid}"] = target

        elif role in ['Virus', 'Wraith']:
            uses = game_state.virus_uses.get(uid, 0) if role == 'Virus' else game_state.wraith_uses.get(uid, 0)
            if uses < 2:
                target = choose_bot_kill_target(game_state, uid, alive_targets)
                game_state.night_actions[f"neutral_kill_{uid}"] = target

        elif role == 'Plague':
            if game_state.plague_infections.get(uid, 0) < 3:
                target = random.choice(alive_targets)[0]
                game_state.night_actions[f"infect_{uid}"] = target

        elif role == 'Volt':
            last_protected = game_state.protection_history.get(uid, [])
            valid_targets = [(uid2, d2) for uid2, d2 in alive_targets if uid2 not in last_protected[-2:]]
            if valid_targets:
                target = random.choice(valid_targets)[0]
                game_state.night_actions[f"protect_{uid}"] = target

        elif role == 'Grid':
            last_scanned = game_state.scan_history.get(uid, [])
            valid_targets = [(uid2, d2) for uid2, d2 in alive_targets if uid2 not in last_scanned[-2:]]
            if valid_targets:
                target = random.choice(valid_targets)[0]
                game_state.night_actions[f"scan_{uid}"] = target

        elif role == 'Bunker':
            last_blocked = game_state.block_history.get(uid, [])
            valid_targets = [(uid2, d2) for uid2, d2 in alive_targets if uid2 not in last_blocked[-2:]]
            if valid_targets:
                target = random.choice(valid_targets)[0]
                game_state.night_actions[f"block_{uid}"] = target

        elif role == 'Sheriff':
            target = choose_bot_kill_target(game_state, uid, alive_targets)
            game_state.night_actions[f"sheriff_{uid}"] = target

def choose_bot_kill_target(game_state, bot_uid, alive_targets):
    memories = get_ai_memories(f"bot_{bot_uid}")
    scores = {}

    for uid, data in alive_targets:
        score = memories.get(uid, 0)

        if data.get('role') in ROLE_POOLS['SURVIVOR_ABILITY']:
            score += SUSPICION_WEIGHTS['ABILITY_USED']

        if data.get('scan_result') == 'SUSPICIOUS':
            score += SUSPICION_WEIGHTS['SCAN_SUSPICIOUS']

        scores[uid] = score

    if scores:
        max_score = max(scores.values())
        top_targets = [uid for uid, score in scores.items() if score == max_score]
        return random.choice(top_targets)

    return random.choice(alive_targets)[0][0]

def schedule_dawn(game_state):
    def dawn_job():
        time.sleep(3)
        resolve_night_actions(game_state)
        start_dawn_phase(game_state)

    Thread(target=dawn_job, daemon=True).start()

def resolve_night_actions(game_state):
    kills = {}
    protects = {}
    blocks = {}
    marks = {}
    infections = {}
    sheriff_kills = {}

    for key, target in game_state.night_actions.items():
        if key.startswith('kill_'):
            killer_uid = int(key.split('_')[1])
            kills[killer_uid] = target
        elif key.startswith('protect_'):
            protector_uid = int(key.split('_')[1])
            protects[protector_uid] = target
        elif key.startswith('block_'):
            blocker_uid = int(key.split('_')[1])
            blocks[blocker_uid] = target
        elif key.startswith('mark_'):
            marker_uid = int(key.split('_')[1])
            marks[marker_uid] = target
        elif key.startswith('infect_'):
            infector_uid = int(key.split('_')[1])
            infections[infector_uid] = target
        elif key.startswith('sheriff_'):
            sheriff_uid = int(key.split('_')[1])
            sheriff_kills[sheriff_uid] = target
        elif key.startswith('neutral_kill_'):
            neutral_uid = int(key.split('_')[1])
            kills[neutral_uid] = target

    blocked_players = set(blocks.values())

    for protector_uid, protected_uid in protects.items():
        if protected_uid in blocked_players:
            try:
                bot.send_message(protector_uid, f"You failed to protect {game_state.get_player_name(protected_uid)} - they were blocked.")
            except Exception:
                pass
        else:
            game_state.night_actions[f"shield_{protected_uid}"] = True
            try:
                bot.send_message(protector_uid, f"You protected {game_state.get_player_name(protected_uid)}.")
            except Exception:
                pass

    for marker_uid, marked_uid in marks.items():
        game_state.marked_players[marked_uid] = True
        game_state.used_abilities[f"phantom_{marker_uid}"] = game_state.used_abilities.get(f"phantom_{marker_uid}", 0) + 1

    for infector_uid, infected_uid in infections.items():
        game_state.infected_players[infected_uid] = True
        game_state.plague_infections[infector_uid] = game_state.plague_infections.get(infector_uid, 0) + 1
        try:
            bot.send_message(infected_uid, PING_PASSIVE_MESSAGE)
        except Exception:
            pass

    dead_this_round = []

    for killer_uid, target_uid in kills.items():
        if target_uid in blocked_players:
            continue

        if game_state.night_actions.get(f"shield_{target_uid}"):
            try:
                bot.send_message(target_uid, f"You survived an attack! Volt's protection held.")
            except Exception:
                pass
            continue

        if target_uid in game_state.players:
            game_state.players[target_uid]['is_alive'] = False
        elif target_uid in game_state.bots:
            game_state.bots[target_uid]['is_alive'] = False

        kill_player(game_state.game_id, target_uid, game_state.current_round)
        dead_this_round.append(target_uid)

        role = game_state.players.get(target_uid, {}).get('role') or game_state.bots.get(target_uid, {}).get('role')
        if role == 'Razor':
            if killer_uid in game_state.players:
                game_state.players[killer_uid]['is_alive'] = False
            elif killer_uid in game_state.bots:
                game_state.bots[killer_uid]['is_alive'] = False
            kill_player(game_state.game_id, killer_uid, game_state.current_round)
            dead_this_round.append(killer_uid)

        log_game_event(game_state.game_id, game_state.current_round, 'KILL', {
            'killer': killer_uid,
            'target': target_uid
        })

    for sheriff_uid, target_uid in sheriff_kills.items():
        if target_uid in blocked_players:
            continue

        target_role = game_state.players.get(target_uid, {}).get('role') or game_state.bots.get(target_uid, {}).get('role')

        if target_role in ['Blackout', 'Razor', 'Phantom', 'Thug']:
            if target_uid in game_state.players:
                game_state.players[target_uid]['is_alive'] = False
            elif target_uid in game_state.bots:
                game_state.bots[target_uid]['is_alive'] = False

            kill_player(game_state.game_id, target_uid, game_state.current_round)
            dead_this_round.append(target_uid)

            try:
                bot.send_message(sheriff_uid, f"Your target {game_state.get_player_name(target_uid)} was Corrupt!")
            except Exception:
                pass

            log_game_event(game_state.game_id, game_state.current_round, 'SHERIFF_KILL', {
                'sheriff': sheriff_uid,
                'target': target_uid,
                'result': 'CORRUPT'
            })
        else:
            if sheriff_uid in game_state.players:
                game_state.players[sheriff_uid]['is_alive'] = False
            elif sheriff_uid in game_state.bots:
                game_state.bots[sheriff_uid]['is_alive'] = False

            kill_player(game_state.game_id, sheriff_uid, game_state.current_round)
            dead_this_round.append(sheriff_uid)

            try:
                bot.send_message(sheriff_uid, f"Your target {game_state.get_player_name(target_uid)} was NOT Corrupt. You died.")
            except Exception:
                pass

            log_game_event(game_state.game_id, game_state.current_round, 'SHERIFF_DEATH', {
                'sheriff': sheriff_uid,
                'target': target_uid,
                'result': 'INNOCENT'
            })

    return dead_this_round

def start_dawn_phase(game_state):
    game_state.current_phase = 'DAWN'

    dead_this_round = []
    for uid, data in game_state.players.items():
        if not data.get('is_alive', True) and data.get('died_at_round') == game_state.current_round:
            dead_this_round.append((uid, data))
    for uid, data in game_state.bots.items():
        if not data.get('is_alive', True) and data.get('died_at_round') == game_state.current_round:
            dead_this_round.append((uid, data))

    if dead_this_round:
        for uid, data in dead_this_round:
            name = game_state.get_player_name(uid)
            bot.send_message(game_state.chat_id, DAWN_MESSAGES['kill'].format(username=name), parse_mode='Markdown')
    else:
        bot.send_message(game_state.chat_id, DAWN_MESSAGES['no_kill'], parse_mode='Markdown')

    win_condition, winner_id = game_state.check_win_condition()
    if win_condition:
        end_game_phase(game_state, win_condition, winner_id)
        return

    start_day_phase(game_state)

def start_day_phase(game_state):
    game_state.current_phase = 'DAY'
    game_state.votes = {}
    game_state.used_abilities = {}

    bot.send_message(game_state.chat_id, "🗣️ *DAY PHASE* - Discuss and vote. 60 seconds.", parse_mode='Markdown')

    for uid, data in game_state.players.items():
        if data.get('is_alive', True) and uid not in game_state.bots:
            update_ai_memory(f"bot_{uid}", uid, 0)

    Thread(target=run_discussion, args=(game_state,), daemon=True).start()

def run_discussion(game_state):
    time.sleep(GAME_SETTINGS['DISCUSSION_TIME'])
    start_voting_phase(game_state)

def start_voting_phase(game_state):
    game_state.current_phase = 'VOTING'

    markup = InlineKeyboardMarkup()
    for uid, data in game_state.get_alive_players():
        name = game_state.get_player_name(uid)
        markup.add(InlineKeyboardButton(f"Vote: {name}", callback_data=f"vote_{uid}"))
    markup.add(InlineKeyboardButton("Skip Vote", callback_data="vote_skip"))

    bot.send_message(game_state.chat_id, "🗳️ *VOTING PHASE* - 30 seconds to vote.", reply_markup=markup, parse_mode='Markdown')

    Thread(target=run_voting, args=(game_state,), daemon=True).start()

def run_voting(game_state):
    time.sleep(GAME_SETTINGS['VOTING_TIME'])
    resolve_votes(game_state)

def resolve_votes(game_state):
    vote_counts = {}
    for voter_uid, target_uid in game_state.votes.items():
        if target_uid == 'skip':
            continue
        vote_counts[target_uid] = vote_counts.get(target_uid, 0) + 1

    if not vote_counts:
        bot.send_message(game_state.chat_id, DAWN_MESSAGES['skip_vote'], parse_mode='Markdown')
        start_night_phase(game_state)
        return

    max_votes = max(vote_counts.values())
    top_targets = [uid for uid, count in vote_counts.items() if count == max_votes]

    if len(top_targets) > 1:
        bot.send_message(game_state.chat_id, DAWN_MESSAGES['tie_vote'], parse_mode='Markdown')
        start_night_phase(game_state)
        return

    exiled_uid = top_targets[0]
    exiled_name = game_state.get_player_name(exiled_uid)
    exiled_role = game_state.players.get(exiled_uid, {}).get('role') or game_state.bots.get(exiled_uid, {}).get('role')

    if exiled_uid in game_state.players:
        game_state.players[exiled_uid]['is_alive'] = False
    elif exiled_uid in game_state.bots:
        game_state.bots[exiled_uid]['is_alive'] = False

    kill_player(game_state.game_id, exiled_uid, game_state.current_round)

    bot.send_message(game_state.chat_id, DAWN_MESSAGES['exile'].format(username=exiled_name, role=exiled_role), parse_mode='Markdown')

    log_game_event(game_state.game_id, game_state.current_round, 'EXILE', {
        'player': exiled_uid,
        'role': exiled_role
    })

    if exiled_role == 'Static':
        for voter_uid in game_state.votes:
            if game_state.votes[voter_uid] == exiled_uid:
                bot.send_message(game_state.chat_id, STATIC_PASSIVE_MESSAGE.format(username=game_state.get_player_name(voter_uid), target=exiled_name), parse_mode='Markdown')
                break

    vote_targets = list(game_state.votes.values())
    if len([v for v in vote_targets if v == exiled_uid]) >= 3:
        bot.send_message(exiled_uid, RELAY_PASSIVE_MESSAGE.format(target=exiled_name))

    win_condition, winner_id = game_state.check_win_condition()
    if win_condition:
        end_game_phase(game_state, win_condition, winner_id)
        return

    start_night_phase(game_state)

def end_game_phase(game_state, winner, winner_id=None):
    game_state.current_phase = 'GAME_END'

    if winner == 'CORRUPT':
        bot.send_message(game_state.chat_id, WIN_MESSAGES['corrupt'], parse_mode='Markdown')
    elif winner == 'SURVIVOR':
        bot.send_message(game_state.chat_id, WIN_MESSAGES['survivor'], parse_mode='Markdown')
    elif winner == 'NEUTRAL':
        winner_name = game_state.get_player_name(winner_id)
        if game_state.players.get(winner_id, {}).get('role') == 'Wraith':
            bot.send_message(game_state.chat_id, WIN_MESSAGES['neutral_wraith'].format(username=winner_name), parse_mode='Markdown')
        else:
            bot.send_message(game_state.chat_id, WIN_MESSAGES['neutral_virus'].format(username=winner_name), parse_mode='Markdown')

    end_game(game_state.game_id, winner, winner_id)

    all_players = game_state.players.copy()
    all_players.update(game_state.bots)

    for uid, data in all_players.items():
        if not game_state.is_ai(uid):
            role = data.get('role')
            won = False
            if winner == 'CORRUPT' and role in ['Blackout', 'Razor', 'Phantom', 'Thug']:
                won = True
            elif winner == 'SURVIVOR' and role in ROLE_POOLS['SURVIVOR_ABILITY'] + ROLE_POOLS['SURVIVOR_VANILLA']:
                won = True
            elif winner == 'NEUTRAL' and uid == winner_id:
                won = True

            elo_change = random.randint(15, 30) if won else -random.randint(10, 25)
            update_player_elo(uid, elo_change)
            increment_player_stats(uid, won)

            try:
                if won:
                    bot.send_message(uid, ELO_MESSAGES['win'].format(
                        old_elo=data.get('elo', 1000),
                        new_elo=data.get('elo', 1000) + elo_change,
                        change=elo_change
                    ))
                else:
                    bot.send_message(uid, ELO_MESSAGES['lose'].format(
                        old_elo=data.get('elo', 1000),
                        new_elo=data.get('elo', 1000) + elo_change,
                        change=elo_change
                    ))
            except Exception:
                pass

    send_game_replay(game_state)

def send_game_replay(game_state):
    game_log = get_game_log(game_state.game_id)

    replay = GAME_REPLAY_HEADER.format(
        game_id=game_state.game_id,
        winner=game_state.current_phase,
        duration=game_state.current_round
    )

    rounds = {}
    for entry in game_log:
        round_num = entry['round_num']
        if round_num not in rounds:
            rounds[round_num] = []
        rounds[round_num].append(entry)

    for round_num, events in sorted(rounds.items()):
        event_texts = []
        for event in events:
            details = eval(event['details']) if isinstance(event['details'], str) else event['details']
            if event['event_type'] == 'KILL':
                killer_name = game_state.get_player_name(details.get('killer', 0))
                target_name = game_state.get_player_name(details.get('target', 0))
                event_texts.append(f"💀 {killer_name} killed {target_name}")
            elif event['event_type'] == 'EXILE':
                player_name = game_state.get_player_name(details.get('player', 0))
                role = details.get('role', 'Unknown')
                event_texts.append(f"🗳️ {player_name} was exiled ({role})")
            elif event['event_type'] == 'SHERIFF_KILL':
                sheriff_name = game_state.get_player_name(details.get('sheriff', 0))
                target_name = game_state.get_player_name(details.get('target', 0))
                event_texts.append(f"⚖️ {sheriff_name} executed {target_name} (Corrupt)")

        if event_texts:
            replay += GAME_REPLAY_ENTRY.format(
                round=round_num,
                events='\n'.join(event_texts)
            )

    bot.send_message(game_state.chat_id, replay, parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Welcome to BLACKOUT. Type /join to enter the lobby.")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, HELP_MESSAGE, parse_mode='Markdown')

@bot.message_handler(commands=['join'])
def join_lobby(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id in game_states and game_states[chat_id].current_phase != 'LOBBY':
        bot.reply_to(message, LOBBY_MESSAGES['game_in_progress'])
        return

    if chat_id not in game_states:
        game_states[chat_id] = GameState(chat_id, user_id, 1)

    game_state = game_states[chat_id]

    if len(game_state.players) + len(game_state.bots) >= GAME_SETTINGS['PLAYER_COUNT']:
        bot.reply_to(message, LOBBY_MESSAGES['lobby_full'])
        return

    if user_id in game_state.players:
        bot.reply_to(message, "You're already in the lobby.")
        return

    game_state.players[user_id] = {
        'name': message.from_user.first_name or message.from_user.username or f'User_{user_id}',
        'role': None,
        'is_alive': True,
        'elo': get_player(user_id)['elo'] if get_player(user_id) else GAME_SETTINGS['INITIAL_ELO']
    }

    save_player(user_id, game_state.players[user_id]['name'])

    count = len(game_state.players) + len(game_state.bots)
    bot.reply_to(message, LOBBY_MESSAGES['join'].format(username=game_state.players[user_id]['name'], count=count))

    if count >= GAME_SETTINGS['PLAYER_COUNT']:
        start_auto_timer(game_state)

@bot.message_handler(commands=['leave'])
def leave_lobby(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in game_states:
        return

    game_state = game_states[chat_id]
    if user_id not in game_state.players:
        return

    name = game_state.players[user_id]['name']
    del game_state.players[user_id]

    count = len(game_state.players) + len(game_state.bots)
    bot.reply_to(message, LOBBY_MESSAGES['leave'].format(username=name, count=count))

@bot.message_handler(commands=['add_bots'])
def add_bots(message):
    chat_id = message.chat.id

    if chat_id not in game_states:
        game_states[chat_id] = GameState(chat_id, message.from_user.id, 1)

    game_state = game_states[chat_id]

    if len(game_state.players) == 0:
        bot.reply_to(message, "❌ At least one human player must join first.")
        return

    current_count = len(game_state.players) + len(game_state.bots)
    bots_needed = GAME_SETTINGS['PLAYER_COUNT'] - current_count

    if bots_needed <= 0:
        bot.reply_to(message, "❌ Lobby is already full.")
        return

    available_names = [name for name in BOT_NAMES if name not in [b['name'] for b in game_state.bots.values()]]
    random.shuffle(available_names)

    for i in range(bots_needed):
        bot_id = f"bot_{i+1}_{chat_id}"
        bot_name = available_names[i] if i < len(available_names) else f"Bot_{i+1}"
        personality = random.choice(BOT_PERSONALITIES)

        game_state.bots[bot_id] = {
            'name': bot_name,
            'role': None,
            'is_alive': True,
            'personality': personality,
            'is_ai': True
        }

        save_player(bot_id, bot_name, True)

    count = len(game_state.players) + len(game_state.bots)
    bot.reply_to(message, f"🤖 Added {bots_needed} bots. ({count}/10)")

    if count >= GAME_SETTINGS['PLAYER_COUNT']:
        start_auto_timer(game_state)

def start_auto_timer(game_state):
    if game_state.auto_start_timer:
        return

    def auto_start():
        for i in range(GAME_SETTINGS['AUTO_START_DELAY'], 0, -1):
            if game_state.current_phase != 'LOBBY':
                return
            if i % 10 == 0 or i <= 5:
                bot.send_message(game_state.chat_id, f"⚡ Game starting in {i} seconds...")
            time.sleep(1)

        if game_state.current_phase == 'LOBBY' and len(game_state.players) + len(game_state.bots) >= 4:
            start_game(game_state)

    game_state.auto_start_timer = Thread(target=auto_start, daemon=True)
    game_state.auto_start_timer.start()

@bot.message_handler(commands=['start_game'])
def start_game_command(message):
    chat_id = message.chat.id

    if chat_id not in game_states:
        return

    game_state = game_states[chat_id]

    if len(game_state.players) + len(game_state.bots) < 4:
        bot.reply_to(message, LOBBY_MESSAGES['not_enough_players'])
        return

    start_game(game_state)

def start_game(game_state):
    game_state.current_phase = 'STARTING'
    game_state.game_start_time = datetime.now()

    game_state.game_id = create_game(game_state.chat_id, game_state.corrupt_count)

    assign_roles(game_state)
    send_role_briefings(game_state)

    bot.send_message(game_state.chat_id, START_TALE, parse_mode='Markdown')

    start_night_phase(game_state)

@bot.message_handler(commands=['corrupt_count'])
def set_corrupt_count(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in game_states:
        return

    game_state = game_states[chat_id]

    if user_id != game_state.creator_id:
        bot.reply_to(message, "❌ Only the game creator can set corrupt count.")
        return

    if game_state.current_phase != 'LOBBY':
        bot.reply_to(message, "❌ Can only set corrupt count during lobby.")
        return

    try:
        count = int(message.text.split()[1])
        if count in [1, 2]:
            game_state.corrupt_count = count
            bot.reply_to(message, LOBBY_MESSAGES['corrupt_count_set'].format(count=count))
        else:
            bot.reply_to(message, "❌ Corrupt count must be 1 or 2.")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Usage: /corrupt_count 1 or /corrupt_count 2")

@bot.message_handler(commands=['players'])
def show_players(message):
    chat_id = message.chat.id

    if chat_id not in game_states:
        bot.reply_to(message, "❌ No game in lobby.")
        return

    game_state = game_states[chat_id]
    player_list = []
    for uid, data in game_state.players.items():
        player_list.append(f"👤 {data['name']}")
    for uid, data in game_state.bots.items():
        player_list.append(f"🤖 {data['name']}")

    count = len(game_state.players) + len(game_state.bots)
    bot.reply_to(message, f"📋 *Players ({count}/10):*\n" + "\n".join(player_list), parse_mode='Markdown')

@bot.message_handler(commands=['vote'])
def vote_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in game_states:
        return

    game_state = game_states[chat_id]

    if game_state.current_phase != 'VOTING':
        bot.reply_to(message, "❌ Can only vote during voting phase.")
        return

    if not game_state.players.get(user_id, {}).get('is_alive', True):
        bot.reply_to(message, "❌ Dead players cannot vote.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Usage: /vote @username")
        return

    target_name = parts[1].lstrip('@')
    target_uid = None

    for uid, data in game_state.get_alive_players():
        if data.get('name', '').lower() == target_name.lower():
            target_uid = uid
            break

    if not target_uid:
        bot.reply_to(message, "❌ Player not found.")
        return

    if target_uid == user_id:
        bot.reply_to(message, "❌ Cannot vote for yourself.")
        return

    game_state.votes[user_id] = target_uid
    bot.send_message(chat_id, VOTE_PUBLIC_MESSAGE.format(
        username=game_state.get_player_name(user_id),
        target=game_state.get_player_name(target_uid)
    ))

@bot.message_handler(commands=['skip'])
def skip_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in game_states:
        return

    game_state = game_states[chat_id]

    if game_state.current_phase != 'VOTING':
        bot.reply_to(message, "❌ Can only skip during voting phase.")
        return

    if not game_state.players.get(user_id, {}).get('is_alive', True):
        bot.reply_to(message, "❌ Dead players cannot vote.")
        return

    game_state.votes[user_id] = 'skip'
    bot.send_message(chat_id, VOTE_SKIP_PUBLIC_MESSAGE.format(username=game_state.get_player_name(user_id)))

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if not player:
        bot.reply_to(message, "❌ You haven't played any games yet.")
        return

    win_rate = (player['wins'] / player['games_played'] * 100) if player['games_played'] > 0 else 0

    bot.reply_to(message, STATS_MESSAGE.format(
        username=player['username'],
        elo=player['elo'],
        games_played=player['games_played'],
        wins=player['wins'],
        win_rate=round(win_rate, 1)
    ), parse_mode='Markdown')

@bot.message_handler(commands=['leaderboard'])
def leaderboard_command(message):
    leaders = get_leaderboard(10)

    if not leaders:
        bot.reply_to(message, "❌ No players yet.")
        return

    entries = []
    for i, player in enumerate(leaders, 1):
        entries.append(LEADERBOARD_ENTRY.format(
            position=i,
            username=player['username'],
            elo=player['elo'],
            wins=player['wins']
        ))

    bot.reply_to(message, LEADERBOARD_MESSAGE.format(entries="\n".join(entries)), parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data

    if chat_id not in game_states:
        bot.answer_callback_query(call.id, "No active game.")
        return

    game_state = game_states[chat_id]

    if not game_state.can_message(user_id):
        bot.answer_callback_query(call.id, "Slow down! Anti-spam active.")
        return

    if data.startswith('kill_'):
        target_uid = int(data.split('_')[1])
        game_state.night_actions[f"kill_{user_id}"] = target_uid
        bot.answer_callback_query(call.id, f"Target selected: {game_state.get_player_name(target_uid)}")
        bot.edit_message_text("✅ Target logged. Awaiting dawn...", chat_id, call.message.message_id)

    elif data.startswith('neutral_kill_'):
        target_uid = int(data.split('_')[2])
        game_state.night_actions[f"neutral_kill_{user_id}"] = target_uid

        role = game_state.players.get(user_id, {}).get('role')
        if role == 'Virus':
            game_state.virus_uses[user_id] = game_state.virus_uses.get(user_id, 0) + 1
        elif role == 'Wraith':
            game_state.wraith_uses[user_id] = game_state.wraith_uses.get(user_id, 0) + 1

        bot.answer_callback_query(call.id, f"Target selected: {game_state.get_player_name(target_uid)}")
        bot.edit_message_text("✅ Target logged. Awaiting dawn...", chat_id, call.message.message_id)

    elif data.startswith('mark_'):
        target_uid = int(data.split('_')[1])
        game_state.night_actions[f"mark_{user_id}"] = target_uid
        bot.answer_callback_query(call.id, f"Marked: {game_state.get_player_name(target_uid)}")
        bot.edit_message_text("✅ Target marked for Corrupt team.", chat_id, call.message.message_id)

    elif data.startswith('protect_'):
        target_uid = int(data.split('_')[1])
        game_state.night_actions[f"protect_{user_id}"] = target_uid

        if user_id not in game_state.protection_history:
            game_state.protection_history[user_id] = []
        game_state.protection_history[user_id].append(target_uid)

        bot.answer_callback_query(call.id, f"Protecting: {game_state.get_player_name(target_uid)}")
        bot.edit_message_text("✅ Protection active. Awaiting dawn...", chat_id, call.message.message_id)

    elif data.startswith('scan_'):
        target_uid = int(data.split('_')[1])
        game_state.night_actions[f"scan_{user_id}"] = target_uid

        if user_id not in game_state.scan_history:
            game_state.scan_history[user_id] = []
        game_state.scan_history[user_id].append(target_uid)

        target_role = game_state.players.get(target_uid, {}).get('role') or game_state.bots.get(target_uid, {}).get('role')
        scan_result = ROLE_DEFINITIONS.get(target_role, {}).get('scan_result', 'CLEAN')

        try:
            bot.send_message(user_id, f"🔍 Scan result: {game_state.get_player_name(target_uid)} is {scan_result}")
        except Exception:
            pass

        bot.answer_callback_query(call.id, "Scan complete.")
        bot.edit_message_text(f"✅ Scan result: {game_state.get_player_name(target_uid)} is {scan_result}", chat_id, call.message.message_id)

    elif data.startswith('block_'):
        target_uid = int(data.split('_')[1])
        game_state.night_actions[f"block_{user_id}"] = target_uid

        if user_id not in game_state.block_history:
            game_state.block_history[user_id] = []
        game_state.block_history[user_id].append(target_uid)

        bot.answer_callback_query(call.id, f"Blocked: {game_state.get_player_name(target_uid)}")
        bot.edit_message_text("✅ Block active. Awaiting dawn...", chat_id, call.message.message_id)

    elif data.startswith('reveal_'):
        target_uid = int(data.split('_')[1])
        game_state.used_abilities[f"kernel_{user_id}"] = True

        target_role = game_state.players.get(target_uid, {}).get('role') or game_state.bots.get(target_uid, {}).get('role')

        try:
            bot.send_message(user_id, f"🔍 {game_state.get_player_name(target_uid)} is {target_role}")
        except Exception:
            pass

        bot.answer_callback_query(call.id, "Role revealed.")
        bot.edit_message_text(f"✅ {game_state.get_player_name(target_uid)} is {target_role}", chat_id, call.message.message_id)

    elif data.startswith('revive_'):
        target_uid = int(data.split('_')[1])
        game_state.used_abilities[f"flare_{user_id}"] = True

        if target_uid in game_state.players:
            game_state.players[target_uid]['is_alive'] = True
        elif target_uid in game_state.bots:
            game_state.bots[target_uid]['is_alive'] = True

        if user_id in game_state.players:
            game_state.players[user_id]['is_alive'] = False
        elif user_id in game_state.bots:
            game_state.bots[user_id]['is_alive'] = False

        kill_player(game_state.game_id, user_id, game_state.current_round)

        try:
            bot.send_message(target_uid, "You have been revived by Flare! You return with no abilities.")
            bot.send_message(user_id, "You sacrificed yourself to revive a fallen player.")
        except Exception:
            pass

        bot.answer_callback_query(call.id, "Player revived.")
        bot.edit_message_text(f"✅ {game_state.get_player_name(target_uid)} has been revived!", chat_id, call.message.message_id)

    elif data.startswith('sheriff_'):
        target_uid = int(data.split('_')[1])
        game_state.night_actions[f"sheriff_{user_id}"] = target_uid
        bot.answer_callback_query(call.id, f"Target selected: {game_state.get_player_name(target_uid)}")
        bot.edit_message_text("✅ Execution ordered. Awaiting dawn...", chat_id, call.message.message_id)

    elif data.startswith('infect_'):
        target_uid = int(data.split('_')[1])
        game_state.night_actions[f"infect_{user_id}"] = target_uid
        bot.answer_callback_query(call.id, f"Infected: {game_state.get_player_name(target_uid)}")
        bot.edit_message_text("✅ Infection spread. Awaiting dawn...", chat_id, call.message.message_id)

    elif data.startswith('steal_'):
        target_uid = int(data.split('_')[1])
        game_state.used_abilities[f"glitch_{user_id}"] = True

        target_role = game_state.players.get(target_uid, {}).get('role') or game_state.bots.get(target_uid, {}).get('role')
        game_state.players[user_id]['role'] = target_role

        try:
            bot.send_message(user_id, f"You stole the {target_role} ability!")
        except Exception:
            pass

        bot.answer_callback_query(call.id, f"Stole {target_role} ability.")
        bot.edit_message_text(f"✅ You now have the {target_role} ability.", chat_id, call.message.message_id)

    elif data == 'vote_skip':
        game_state.votes[user_id] = 'skip'
        bot.send_message(chat_id, VOTE_SKIP_PUBLIC_MESSAGE.format(username=game_state.get_player_name(user_id)))
        bot.answer_callback_query(call.id, "Vote skipped.")

    elif data.startswith('vote_'):
        target_uid = int(data.split('_')[1])
        game_state.votes[user_id] = target_uid
        bot.send_message(chat_id, VOTE_PUBLIC_MESSAGE.format(
            username=game_state.get_player_name(user_id),
            target=game_state.get_player_name(target_uid)
        ))
        bot.answer_callback_query(call.id, f"Voted for {game_state.get_player_name(target_uid)}")

@bot.message_handler(commands=['spectate'])
def spectate_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if chat_id not in game_states:
        bot.reply_to(message, "❌ No game in progress.")
        return

    game_state = game_states[chat_id]

    player_data = game_state.players.get(user_id) or game_state.bots.get(user_id)
    if player_data and player_data.get('is_alive', True):
        bot.reply_to(message, "❌ You're still alive! Wait until you're eliminated.")
        return

    bot.reply_to(message, DEAD_SPECTATE_MESSAGE, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in game_states:
        return

    game_state = game_states[chat_id]

    if not game_state.can_message(user_id):
        return

    if game_state.current_phase == 'DAY':
        player_data = game_state.players.get(user_id) or game_state.bots.get(user_id)
        if player_data and not player_data.get('is_alive', True):
            return

        name = game_state.get_player_name(user_id)
        bot.send_message(chat_id, f"🗣️ {name}: {message.text}")

def run_bot_chat(game_state):
    if game_state.current_phase != 'DAY':
        return

    for uid, data in game_state.bots.items():
        if not data.get('is_alive', True):
            continue

        if random.random() > 0.4:
            continue

        personality = data.get('personality', 'Quiet')
        templates = BOT_CHAT_TEMPLATES.get(personality, BOT_CHAT_TEMPLATES['Quiet'])

        alive_players = game_state.get_alive_players()
        other_players = [(uid2, d2) for uid2, d2 in alive_players if uid2 != uid]

        if not other_players:
            continue

        target_uid, target_data = random.choice(other_players)
        target_name = game_state.get_player_name(target_uid)

        action = random.choice(['accuse', 'agree', 'quiet'])
        template = templates.get(action, templates['quiet'])

        chat_text = template.format(
            bot=data['name'],
            target=target_name,
            accuser=random.choice([d2['name'] for uid2, d2 in other_players if uid2 != target_uid]) if other_players else 'someone'
        )

        bot.send_message(game_state.chat_id, chat_text, parse_mode='Markdown')
        time.sleep(random.uniform(1, 3))

def run_periodic_bot_chat(game_state):
    while game_state.current_phase in ['DAY', 'VOTING']:
        run_bot_chat(game_state)
        time.sleep(random.uniform(5, 10))

print("🤖 BLACKOUT Production Engine Operational...")
init_db()
bot.infinity_polling()
