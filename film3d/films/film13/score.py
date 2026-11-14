def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 0.5), 0, 0.2)
    S.train_rhythm(0.0, 33.4, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 3.6, 0.38, 0.12)     # THEME once
    for k in range(6): S.add(S.clack(), 5.6 + k * 0.33, 0.18, -0.3)                             # the lamps behind die
    S.add(S.drone(14.0, 38), 5.8, 0.5)
    S.add(S.shh(2.0), 6.8, 0.5); S.add(S.stinger(), 7.6, 0.55)                                   # its face over the ridge
    S.add(S.whistle(1.4), 11.2, 0.8)
    S.train_rhythm(11.2, 33.2, 0.28, 0.15); S.chase(11.4, 30.4, bpm=160, gain=0.14)
    S.steps(9.0, 42.0, 0.8, 0.55)                                                                # it comes down the valley
    S.add(S.wind(70.0, 1.6), 22.0, 0.35)                                                         # the roar of the falls grows
    S.add(S.thump(), 33.4, 0.5)                                                                  # our lights out
    S.silence_music(33.4, 62.4, 0.9)
    S.add(S.drone(16.0, 36), 34.0, 0.4)
    S.steps(42.0, 48.0, 1.2, 0.5)
    S.add(S.drone(9.0, 33), 44.6, 0.5)
    for k in range(13): S.add(S.heartbeat(), 46.0 + k * 0.72, 0.45 if k < 5 else 0.6)
    S.add(S.shh(2.4), 49.2, 0.5); S.add(S.shh(2.4), 53.0, 0.45)
    S.add(S.stinger(), 55.4, 0.6); S.add(S.thump(), 55.5, 0.7)                                   # the cold water hits its mask
    S.steps(57.0, 70.0, 1.6, 0.35)                                                               # it walks off down the river
    S.add(S.whistle(1.8), 62.8, 0.85)
    S.train_rhythm(63.2, 96.0, 0.26, 0.15); S.chase(63.6, 86.0, bpm=168, gain=0.14)
    S.add(S.stinger(), 75.6, 0.5)                                                                # it turns back and follows
    S.steps(74.0, 95.0, 1.0, 0.4)
    S.add(S.whistle(1.2), 89.5, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 91.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 95.0, 0.5, 0.11)
