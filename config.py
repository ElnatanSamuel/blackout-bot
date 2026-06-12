import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_FALLBACK_TOKEN_IF_LOCAL')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'blackout.db')

GAME_SETTINGS = {
    'PLAYER_COUNT': 10,
    'DISCUSSION_TIME': 60,
    'VOTING_TIME': 30,
    'AUTO_START_DELAY': 30,
    'ANTI_SPAM_COOLDOWN': 2,
    'BOT_SPAM_COOLDOWN': 3,
    'INITIAL_ELO': 1000
}

ROLE_POOLS = {
    'CORRUPT': ['Blackout', 'Razor', 'Phantom', 'Thug'],
    'NEUTRAL': ['Virus', 'Wraith', 'Glitch', 'Plague'],
    'SURVIVOR_ABILITY': ['Volt', 'Grid', 'Bunker', 'Kernel', 'Flare', 'Sheriff'],
    'SURVIVOR_VANILLA': ['Static', 'Relay', 'Ping']
}

ROLE_DEFINITIONS = {
    'Blackout': {
        'team': 'CORRUPT',
        'can_kill': True,
        'scan_result': 'CLEAN',
        'unique': False,
        'ability': 'Kill one player per night',
        'limitation': 'Only CLEAN Corrupt'
    },
    'Razor': {
        'team': 'CORRUPT',
        'can_kill': True,
        'scan_result': 'SUSPICIOUS',
        'unique': True,
        'ability': 'Kill one player per night. If killed, attacker dies too',
        'limitation': 'Revenge kill'
    },
    'Phantom': {
        'team': 'CORRUPT',
        'can_kill': False,
        'scan_result': 'SUSPICIOUS',
        'unique': True,
        'ability': 'Mark one ability player per 2 rounds. Mark visible to Corrupt after 1 day',
        'limitation': 'Support role'
    },
    'Thug': {
        'team': 'CORRUPT',
        'can_kill': True,
        'scan_result': 'SUSPICIOUS',
        'unique': False,
        'ability': 'Kill one player per night (basic)',
        'limitation': 'No special ability'
    },
    'Virus': {
        'team': 'NEUTRAL',
        'can_kill': True,
        'scan_result': 'SUSPICIOUS',
        'unique': True,
        'ability': '2-use night kill with cooldown',
        'limitation': 'Must kill 3 assigned targets'
    },
    'Wraith': {
        'team': 'NEUTRAL',
        'can_kill': True,
        'scan_result': 'SUSPICIOUS',
        'unique': True,
        'ability': '2-use night kill with cooldown',
        'limitation': 'Must be last alive'
    },
    'Glitch': {
        'team': 'NEUTRAL',
        'can_kill': False,
        'scan_result': 'SUSPICIOUS',
        'unique': True,
        'ability': 'Steal one dead player\'s ability (one-time use)',
        'limitation': 'Must survive + use stolen ability'
    },
    'Plague': {
        'team': 'NEUTRAL',
        'can_kill': False,
        'scan_result': 'SUSPICIOUS',
        'unique': True,
        'ability': 'Infect one player nightly. Infected players lose next action',
        'limitation': 'Must infect 3 players total'
    },
    'Volt': {
        'team': 'SURVIVOR',
        'can_kill': False,
        'scan_result': 'CLEAN',
        'unique': True,
        'ability': 'Protect one player nightly',
        'limitation': 'Can\'t self-protect. Can\'t same player 2x row. SUSPICIOUS on use'
    },
    'Grid': {
        'team': 'SURVIVOR',
        'can_kill': False,
        'scan_result': 'CLEAN',
        'unique': True,
        'ability': 'Night scan: CLEAN or SUSPICIOUS',
        'limitation': 'Can\'t scan same player 2x row. SUSPICIOUS on use'
    },
    'Bunker': {
        'team': 'SURVIVOR',
        'can_kill': False,
        'scan_result': 'CLEAN',
        'unique': True,
        'ability': 'Role-block one player nightly',
        'limitation': 'Can\'t block same player 2x row'
    },
    'Kernel': {
        'team': 'SURVIVOR',
        'can_kill': False,
        'scan_result': 'CLEAN',
        'unique': True,
        'ability': 'One-time: reveal exact role',
        'limitation': 'One-time. Can\'t use on self'
    },
    'Flare': {
        'team': 'SURVIVOR',
        'can_kill': False,
        'scan_result': 'CLEAN',
        'unique': True,
        'ability': 'One-time: revive one dead player',
        'limitation': 'Dies. Revived returns no abilities'
    },
    'Sheriff': {
        'team': 'SURVIVOR',
        'can_kill': True,
        'scan_result': 'SUSPICIOUS',
        'unique': True,
        'ability': 'Kill one player nightly',
        'limitation': 'If target not Corrupt, Sheriff dies. No kill limit'
    },
    'Static': {
        'team': 'SURVIVOR',
        'can_kill': False,
        'scan_result': 'SUSPICIOUS',
        'unique': False,
        'ability': 'First vote against them is public',
        'limitation': 'Vanilla with passive'
    },
    'Relay': {
        'team': 'SURVIVOR',
        'can_kill': False,
        'scan_result': 'CLEAN',
        'unique': False,
        'ability': 'If 3+ vote same target, that target learns who voted',
        'limitation': 'Vanilla with passive'
    },
    'Ping': {
        'team': 'SURVIVOR',
        'can_kill': False,
        'scan_result': 'CLEAN',
        'unique': False,
        'ability': 'First time targeted: notification YOU WERE TARGETED',
        'limitation': 'Vanilla with passive'
    }
}

BOT_NAMES = [
    'Alex', 'Jordan', 'Sam', 'Riley', 'Casey', 'Morgan', 'Taylor',
    'Quinn', 'Avery', 'Drew', 'Jamie', 'Sage', 'Reese', 'Finley',
    'Hayley', 'Devon', 'Kelsey', 'Logan', 'Parker', 'Blake',
    'Charlie', 'Skyler', 'Dakota', 'Reagan', 'Cameron', 'Emery',
    'Rowan', 'Phoenix', 'River', 'Sawyer', 'Ellis', 'Jesse'
]

BOT_PERSONALITIES = ['Aggressive', 'Cautious', 'Quiet', 'Strategic']

SUSPICION_WEIGHTS = {
    'ABILITY_USED': 1,
    'SCAN_SUSPICIOUS': 2,
    'VOTE_WITH_CORRUPT': 3,
    'PROTECTED_BY_VOLT': -1,
    'ACCUSED_BY': 2
}
