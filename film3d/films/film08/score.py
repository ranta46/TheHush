def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 0.7), 0, 0.22)   # night wind over the plain
    S.train_rhythm(0.0, 28.5, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 3.8, 0.38, 0.12)    # THEME once
    for k in range(6): S.add(S.clack(), 8.0 + k * 0.5, 0.18, -0.5)                              # the lamps behind us die
    S.add(S.drone(16.0, 38), 9.0, 0.5)
    S.add(S.shh(2.0), 12.4, 0.5); S.add(S.stinger(), 13.6, 0.55)                               # it rises behind us
    S.add(S.whistle(1.4), 16.0, 0.8)
    S.train_rhythm(16.0, 28.0, 0.28, 0.15); S.chase(16.5, 28.0, bpm=160, gain=0.14)
    S.steps(15.5, 31.5, 0.8, 0.55)                                                              # it runs after us
    for k in range(3): S.add(S.clack(), 27.0 + k * 0.4, 0.5)                                    # brakes at the power house
    S.add(S.thump(), 30.6, 0.7)                                                                 # the big switch
    for k in range(8): S.add(S.clack(), 31.0 + k * 0.35, 0.25, -0.6 + k * 0.17)                 # the city wakes, street by street
    S.play([(74, 1), (78, 1), (81, 2)], 31.2, 0.3, 0.12)
    S.add(S.thump(), 35.5, 0.5)                                                                 # our lights out
    S.silence_music(35.5, 66.4, 0.95)
    S.add(S.drone(30.0, 33), 36.0, 0.55)
    S.steps(38.0, 46.0, 1.1, 0.45)
    for k in range(6): S.add(S.clack(), 38.5 + k * 1.2, 0.07, 0.2)                              # wheels, very soft
    for k in range(4): S.add(S.clack(), 40.5 + k * 0.12, 0.2, -0.4)                             # the first street dies
    for k in range(18): S.add(S.heartbeat(), 45.0 + k * 0.72, 0.45 if k < 8 else 0.6)
    S.add(S.shh(2.4), 47.5, 0.5); S.add(S.shh(2.4), 52.5, 0.45)
    for k in range(4): S.add(S.clack(), 50.5 + k * 0.12, 0.2, -0.4)
    S.steps(55.5, 64.2, 1.2, 0.4)                                                               # it walks deeper in
    for k in range(5): S.add(S.clack(), 57.0 + k * 1.2, 0.06, 0.2)
    for t in (58.0, 61.0): S.add(S.clack(), t, 0.2, -0.5)
    S.add(S.drone(3.0, 30), 64.0, 0.6); S.add(S.stinger(), 64.3, 0.6)                           # the whole city dies at once
    S.add(S.whistle(1.8), 67.2, 0.85)
    S.train_rhythm(67.4, 97.5, 0.26, 0.15); S.chase(68.0, 88.0, bpm=168, gain=0.14)
    S.steps(66.5, 92.0, 0.8, 0.5)                                                               # it follows us
    for k in range(8): S.add(S.clack(), 80.5 + k * 0.6, 0.2, 0.3)                               # over the iron bridge
    S.add(S.whistle(1.2), 89.5, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 91.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 95.0, 0.5, 0.11)
