import copy

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
        "team_size": 15
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 40,
        "radius_max": 55,
        "health": 340,
        "dmg_multiplier": 1.5,
        "luck": 10,
        "team_size": 15
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 50,
        "radius_max": 60,
        "health": 120,
        "dmg_multiplier": 1,
        "luck": 15,
        "team_size": 15
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 30,
        "radius_max": 40,
        "health": 160,
        "dmg_multiplier": 2.5,
        "luck": 12,
        "team_size": 15
    },
    {
        "density": 1,
        "velocity": 4,
        "radius_min": 75,
        "radius_max": 80,
        "health": 750,
        "dmg_multiplier": 1.5,
        "luck": 8,
        "team_size": 5
    },
]
circles_unchanged = copy.deepcopy(circles)