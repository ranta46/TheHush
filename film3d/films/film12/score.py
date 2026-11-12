def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 0.7), 0, 0.24)    # mountain wind
    S.train_rhythm(0.0, 40.2, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 3.6, 0.38, 0.12)     # THEME once
    for k in range(7): S.add(S.clack(), 5.6 + k * 0.33, 0.18, -0.3)                             # the valley lamps die in a wave
    S.add(S.drone(14.0, 38), 5.8, 0.5)
    S.add(S.shh(2.0), 6.8, 0.5); S.add(S.stinger(), 7.6, 0.55)                                   # its face over the ridge
    S.add(S.whistle(1.4), 11.2, 0.8)
    S.train_rhythm(11.2, 40.0, 0.28, 0.15); S.chase(11.4, 26.4, bpm=160, gain=0.14)
    S.steps(9.0, 31.4, 0.8, 0.55)                                                                # it comes up the valley
    S.add(S.whistle(2.6), 27.0, 0.95)                                                            # the long whistle
    S.add(S.thump(), 28.4, 0.6); S.add(S.thump(), 29.2, 0.7); S.add(S.thump(), 30.2, 0.8)       # the snow comes down
    S.add(S.drone(5.0, 33), 28.4, 0.6)
    S.silence_music(31.0, 36.0, 0.6)
    S.steps(36.0, 46.0, 1.4, 0.4)                                                                # it climbs over the ridge
    S.add(S.stinger(), 38.8, 0.45)
    S.add(S.thump(), 40.2, 0.5)                                                                  # our lights out
    S.silence_music(40.2, 61.4, 0.9)
    S.add(S.drone(16.0, 36), 40.6, 0.4)
    for k in range(2): S.add(S.clack(), 46.2 + k * 2.2, 0.4, 0.3)                               # the ledge lamps die
    S.steps(46.0, 50.0, 1.0, 0.5)
    S.add(S.drone(9.0, 33), 48.0, 0.5)
    for k in range(13): S.add(S.heartbeat(), 47.6 + k * 0.72, 0.45 if k < 5 else 0.6)
    S.add(S.shh(2.4), 49.2, 0.5); S.add(S.shh(2.4), 54.0, 0.45)
    S.add(S.thump(), 57.3, 0.8); S.add(S.drone(4.0, 31), 57.3, 0.6)                             # the snow gives way under it
    for k in range(5): S.add(S.thump(), 57.8 + k * 0.6, 0.5 - k * 0.06)                         # it slides over the shed and down
    S.add(S.whistle(1.8), 61.8, 0.85)
    S.train_rhythm(62.2, 96.0, 0.26, 0.15); S.chase(62.6, 86.0, bpm=168, gain=0.14)
    S.add(S.stinger(), 73.4, 0.5)                                                                # it climbs back up and follows
    S.steps(70.0, 95.0, 1.0, 0.4)
    S.add(S.whistle(1.2), 89.5, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 91.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 95.0, 0.5, 0.11)
