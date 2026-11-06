def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 0.9), 0, 0.28)   # wind over the high moor
    S.train_rhythm(0.0, 15.5, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 3.8, 0.38, 0.12)    # THEME once
    for k in range(6): S.add(S.clack(), 9.0 + k * 0.5, 0.18, 0.5)                               # the valley lamps die
    S.add(S.drone(14.0, 38), 9.5, 0.5)
    for k in range(3): S.add(S.clack(), 13.2 + k * 0.4, 0.5)                                    # brakes at the top
    S.add(S.shh(2.0), 12.4, 0.5); S.add(S.stinger(), 14.0, 0.55)                               # it rises down there
    S.steps(19.0, 64.8, 1.0, 0.5)                                                               # it climbs the hill
    S.add(S.thump(), 29.3, 0.6)                                                                 # the firebox door shuts
    for k in range(3): S.add(S.clack(), 30.0 + k * 0.4, 0.35, -0.3)                             # our lights go out
    S.silence_music(29.5, 67.6, 0.95)
    S.add(S.drone(36.0, 33), 31.0, 0.6)
    for k in range(10): S.add(S.clack(), 33.0 + k * 3.0, 0.08, 0.2)                             # wheels, very soft, rolling
    for k in range(22): S.add(S.heartbeat(), 44.0 + k * 0.72, 0.45 if k < 10 else 0.6)
    S.add(S.shh(2.4), 47.0, 0.5); S.add(S.shh(2.4), 52.0, 0.45)
    for k in range(20): S.add(S.bell(88, 0.5), 64.8 + k * 0.5, 0.35, 0.4)                       # the old crossing bell: ding, ding
    S.add(S.stinger(), 66.5, 0.5)
    S.add(S.whistle(1.8), 68.2, 0.85)
    S.train_rhythm(68.5, 97.5, 0.26, 0.15); S.chase(69.0, 86.0, bpm=168, gain=0.14)
    S.steps(67.5, 96.0, 0.8, 0.5)                                                               # it walks down after us
    S.add(S.whistle(1.2), 90.0, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 91.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 95.0, 0.5, 0.11)
