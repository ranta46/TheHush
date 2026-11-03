def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 1.2), 0, 0.3)   # sea wind
    S.train_rhythm(0.0, 24.0, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 4.5, 0.38, 0.12)   # THEME once
    S.add(S.bell(62, 4.0), 9.3, 0.22, -0.7)                                                     # far lighthouse bell, then nothing
    for k in range(6): S.add(S.clack(), 14.8 + k * 0.3, 0.22, -0.3)                             # track lamps die
    S.add(S.drone(12.0, 38), 15.0, 0.5)
    S.add(S.shh(2.0), 25.0, 0.5); S.add(S.stinger(), 27.3, 0.55)                               # it rises out of the sea
    S.add(S.whistle(1.4), 31.4, 0.75)
    S.train_rhythm(31.4, 47.0, 0.24, 0.16); S.chase(31.6, 46.4, bpm=164, gain=0.15)
    S.steps(30.0, 46.0, 0.8, 0.55)
    S.add(S.clack(), 46.3, 0.8); S.add(S.clack(), 46.5, 0.7)                                    # lights off
    S.silence_music(46.5, 78.5, 0.95)
    S.add(S.drone(31.0, 33), 47.0, 0.8)
    S.steps(47.0, 61.0, 1.2, 0.45)
    for k in range(14): S.add(S.heartbeat(), 61.0 + k * 0.75, 0.5 if k < 7 else 0.6)
    S.add(S.shh(2.4), 58.0, 0.5); S.add(S.shh(2.4), 66.0, 0.45)
    S.add(S.wind(3.0, 2.0), 71.8, 0.45, -0.6); S.add(S.whistle(0.9), 72.2, 0.18, -0.6)            # Old Nine hisses
    S.add(S.thump(), 73.6, 0.4); S.steps(73.6, 79.0, 1.0, 0.4)                                   # it turns to Old Nine
    S.train_rhythm(76.5, 79.0, 0.55, 0.06)                                                       # quiet wheels
    S.add(S.whistle(1.8), 79.2, 0.85)
    S.train_rhythm(79.2, dur - 0.5, 0.26, 0.15); S.chase(79.4, 86.0, bpm=168, gain=0.14)
    S.add(S.shh(1.6), 85.4, 0.35, -0.5)                                                         # it eats Old Nine's light
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 87.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 92.0, 0.5, 0.11)
