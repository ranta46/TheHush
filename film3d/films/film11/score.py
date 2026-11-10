def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 0.7), 0, 0.22)    # night wind on the heath
    S.train_rhythm(0.0, 25.8, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 3.6, 0.38, 0.12)     # THEME once
    for k in range(6): S.add(S.clack(), 5.4 + k * 0.45, 0.18, -0.3)                             # the hill lamps die
    S.add(S.drone(14.0, 38), 5.8, 0.5)
    S.add(S.shh(2.0), 6.8, 0.5); S.add(S.stinger(), 7.6, 0.55)                                   # its face over the hilltop
    S.add(S.whistle(1.4), 11.6, 0.8)
    S.train_rhythm(11.6, 25.8, 0.28, 0.15); S.chase(11.8, 26.0, bpm=160, gain=0.14)
    S.steps(9.0, 25.6, 0.8, 0.55)                                                                # it comes round the hill
    for k in range(3): S.add(S.clack(), 20.6 + k * 1.2, 0.2, 0.4)                               # the line lamps behind us die
    S.add(S.thump(), 26.0, 0.5)                                                                  # our lights out
    S.silence_music(26.0, 61.4, 0.9)
    S.add(S.drone(16.0, 36), 26.4, 0.4)
    S.steps(26.0, 40.0, 1.6, 0.35)                                                               # it searches round the far side
    for k in range(4): S.add(S.clack(), 42.9 + k * 0.6, 0.45, -0.3)                             # the stuck lever
    S.steps(40.0, 50.0, 1.0, 0.5)                                                                # it comes round to us
    S.add(S.drone(12.0, 33), 45.0, 0.5)
    for k in range(14): S.add(S.heartbeat(), 47.0 + k * 0.72, 0.45 if k < 6 else 0.6)
    S.add(S.shh(2.4), 48.6, 0.5); S.add(S.shh(2.4), 53.6, 0.45)
    S.add(S.bell(86, 3.0), 56.6, 0.25, 0.4); S.add(S.bell(93, 3.0), 57.0, 0.18, 0.6)            # the falling star
    S.steps(57.4, 66.5, 1.2, 0.4)                                                                # it walks off after the light
    S.add(S.clack(), 61.2, 0.7, -0.3); S.add(S.thump(), 61.4, 0.6)                              # the switch gives
    S.add(S.whistle(1.8), 61.8, 0.85)
    S.train_rhythm(62.2, 96.0, 0.26, 0.15); S.chase(62.6, 86.0, bpm=168, gain=0.14)
    S.add(S.stinger(), 72.8, 0.5)                                                                # it turns and follows
    S.steps(70.0, 95.0, 1.0, 0.4)
    S.add(S.whistle(1.2), 89.5, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 91.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 95.0, 0.5, 0.11)
