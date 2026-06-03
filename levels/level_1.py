import numpy as np
LEVEL = [
    {
        "name": "IJN Yamato",
        "x": 600, "y": -400,
        "frnd": "enemy",
        "behavior": "patrol",
        "waypoints": [(600, -400), (1000, -100), (600, 300), (200, -100)],
        "shoot_times": np.arange(0, 3600, 600)
    },
    {
        "name": "Bismarck",
        "x": -500, "y": 300,
        "frnd": "enemy",
        "behavior": "chase",
        "shoot_times": np.arange(0, 3600, 800)
    },
    {
        "name": "Musashi",
        "x": 200, "y": -900,
        "frnd": "enemy",
        "behavior": "idle",
    },
]
