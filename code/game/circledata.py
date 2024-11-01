import copy

titles = ["Rookie", "Novice", "Apprentice", "Journeyman", "Adept", "Veteran", "Master", "Grandmaster", "Champion", "Legend", "Hero", "Myth", "Titan", "Demigod", "Immortal", "Warlord", "Overlord", "Conqueror", "Tyrant", "Sovereign", "Emperor", "Supreme", "Almighty", "Invincible", "Colossus", "Behemoth", "Dreadnought", "Archon", "Ascendant", "Godlike"]

names = ["Zippy", "Bixie", "Jazzy", "Quirk", "Fizzy", "Zazzy", "Pixel", "Zippy", "Jazzy", "Fizzy", "Quixy", "Vixen", "Zesty", "Pixel", "Zilch", "Zonky", "Flick", "Quirk", "Zappy", "Zippy", "Pixel", "Bixby", "Zilch", "Vixen", "Jazzy", "Zesty", "Fizzy", "Bixby", "Pixel", "Quixy", "Zilch", "Zappy", "Flick", "Zesty", "Zippy", "Quirk", "Jazzy", "Pixel", "Bixie", "Fizzy", "Quixy", "Zappy", "Vixen", "Jazzy", "Pixel", "Flick", "Bixie", "Zilch", "Quirk", "Zesty", "Jazzy", "Pixel", "Zappy", "Bixie", "Flick", "Quixy", "Zilch", "Vixen", "Zesty", "Fizzy", "Bixby", "Pixel", "Zappy", "Zippy", "Jazzy", "Quixy", "Flick", "Zilch", "Pixel", "Zappy", "Bixie", "Fizzy", "Jazzy", "Quirk", "Zesty", "Pixel", "Flick", "Bixie", "Zappy", "Quixy", "Zilch", "Jazzy", "Fizzy", "Zesty", "Pixel", "Zappy", "Bixby", "Quirk", "Flick", "Zilch", "Jazzy", "Quixy", "Pixel", "Fizzy", "Bixie", "Zappy", "Zesty", "Jazzy", "Quirk", "Flick", "Zok", "Fip", "Zim", "Zat", "Qip", "Dax", "Zin", "Kip", "Zor", "Qik", "Piz", "Tix", "Zab", "Wop", "Qoz", "Dib", "Zep", "Fop", "Zem", "Jip", "Qub", "Vex", "Zed", "Qet", "Wix", "Zin", "Joz", "Zim", "Fex", "Qix", "Zep", "Wox", "Piz", "Qub", "Zun", "Jex", "Zil", "Qop", "Vip", "Zeb", "Qix", "Vom", "Zit", "Zuv", "Qol", "Zok", "Jip", "Qub", "Zet", "Piz", "Qat", "Zim", "Qab", "Zuz", "Qip", "Zeb", "Fiz", "Qix", "Zun", "Pov", "Zat", "Qor", "Zep", "Qux", "Zol", "Qix", "Zem", "Juz", "Qab", "Zet", "Zix", "Qox", "Zop", "Qut", "Zun", "Qix", "Zex", "Qob", "Zit", "Jix", "Qiz", "Zup", "Qix", "Zem", "Zat", "Qop", "Zob", "Qix", "Zat", "Qid", "Zux", "Qub", "Zut", "Qix", "Zem", "Qod", "Zex", "Qip", "Zop", "Qiz"]

# CUMULATIVE AMOUNTS (LEVEL 2 = 10-19)
xp_amounts = [10, 20, 30, 40, 50, 60, 70, 80, 90]

powerup_data = {

    "skull":        ["assets/powerups/skull.png",        0],
    "resurrect":    ["assets/powerups/wings.png",        1],
    "star":         ["assets/powerups/star.png",         2],
    "boxing_glove": ["assets/powerups/boxing_glove.png", 3],
    "feather":      ["assets/powerups/feather.png",      4],
    "cherry":       ["assets/powerups/cherry.png",       5],
    "bomb":         ["assets/powerups/bomb.png",         6],
    "laser":        ["assets/powerups/green_laser.png",  7],
    "buckshot":     ["assets/powerups/purple_laser.png", 8],
}

colors = [
    # SPECIAL COLORS - TAKE CARE
    ["rainbow", "gradient1.png", (255, 180, 180)],
    ["grayscale", "gradient2.png", (100, 100, 100)],
    ["rose", "gradient3.png", (255, 51, 153)],
    ["lavender", "gradient4.png", (153, 153, 255)],
    ["mint", "gradient5.png", (0, 255, 128)],
    ["violet", "gradient6.png", (204, 28, 134)],
    ["sunrise", "gradient7.png", (223, 143, 15)],
    ["clay", "gradient8.png", (140, 70, 70)],
    ["sky", "gradient9.png", (49, 142, 172)],
    ["algae", "gradient10.png", (16, 143, 22)],
    ["bog", "gradient11.png", (160, 123, 107)],
    ["wound", "gradient12.png", (209, 33, 34)],
    ["dusk", "gradient13.png", (61, 62, 128)],
    ["rainier", "gradient14.png", (189, 126, 147)],
    ["midnight", "gradient15.png", (18, 18, 18)],
    ["eggshell", "gradient16.png", (138, 116, 122)],
    ["bruise", "gradient17.png", (92, 50, 124)],
]

mins = {
    "density": 1,
    "velocity": 1,
    "radius": 5,
    "health": 25,
    "dmg_multiplier": 0.1,
    "luck": 1,
}

maxes = {
    "density": 99,
    "velocity": 9,
    "radius": 300,
    "health": 999,
    "dmg_multiplier": 9.9,
    "luck": 99,
}

circles = [
    {
        "density": 1,
        "velocity": 3,
        "radius_min": 30,
        "radius_max": 45,
        "health": 260,
        "dmg_multiplier": 1.7,
        "luck": 8,
        "team_size": 15,
        "name": "glee"
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 40,
        "radius_max": 55,
        "health": 340,
        "dmg_multiplier": 1.5,
        "luck": 10,
        "team_size": 15,
        "name": "stale"
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 50,
        "radius_max": 60,
        "health": 120,
        "dmg_multiplier": 1,
        "luck": 15,
        "team_size": 15,
        "name": "grinn"
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 30,
        "radius_max": 40,
        "health": 160,
        "dmg_multiplier": 2.5,
        "luck": 12,
        "team_size": 15,
        "name": "dink"
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 75,
        "radius_max": 80,
        "health": 750,
        "dmg_multiplier": 1.5,
        "luck": 8,
        "team_size": 5,
        "name": "mech"
    },
]
circles_unchanged = copy.deepcopy(circles)