def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur), 0, 0.3)
    S.train_rhythm(0.0, 14.4, 0.42, 0.14)
    for k in range(10): S.add(S.clack(), 9.0 + k * 0.42 + 0.25, 0.08, 0.6 if k % 2 else -0.6)   # the walls sing the wheels back
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 4.5, 0.38, 0.12)   # THEME once
    for k in range(6): S.add(S.clack(), 14.4 + k * 0.3, 0.22, 0.3)                              # track lamps die
    S.train_rhythm(14.4, 24.0, 0.42, 0.10)                                                       # no echo now
    S.add(S.drone(12.0, 38), 15.0, 0.5)
    S.add(S.shh(2.0), 26.0, 0.5); S.add(S.stinger(), 28.5, 0.55)                                # its eyes open
    S.add(S.whistle(1.4), 32.0, 0.75)
    S.train_rhythm(32.0, 54.0, 0.24, 0.16); S.chase(32.2, 50.0, bpm=160, gain=0.14)
    S.steps(30.0, 44.0, 0.8, 0.5)
    S.add(S.whistle(3.0), 44.8, 0.95)                                                            # the long whistle
    for k, (dt, g, p) in enumerate(((1.4, 0.45, 0.7), (2.9, 0.32, -0.7), (4.5, 0.22, 0.8), (6.2, 0.14, -0.8))):
        S.add(S.whistle(2.6), 44.8 + dt, g, p)                                                   # its echo, again and again
    S.steps(46.5, 56.0, 1.0, 0.35)
    S.add(S.shh(2.4), 56.0, 0.5)
    S.silence_music(57.0, 74.5, 0.95)
    S.add(S.drone(17.0, 33), 57.5, 0.8)
    S.steps(59.5, 64.0, 1.2, 0.5)
    for k in range(10): S.add(S.heartbeat(), 64.0 + k * 0.7, 0.5 if k < 5 else 0.6)
    S.add(S.shh(2.4), 66.5, 0.45)
    S.add(S.whistle(3.0), 70.6, 0.12, -0.8); S.add(S.whistle(2.6), 72.0, 0.07, 0.8)               # the old echo, far away
    S.steps(73.0, 80.0, 1.1, 0.35)
    S.train_rhythm(75.0, 78.0, 0.5, 0.08)
    S.add(S.whistle(1.8), 78.0, 0.9)
    S.train_rhythm(78.0, dur - 0.5, 0.26, 0.15); S.chase(78.2, 86.0, bpm=168, gain=0.15)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 86.5, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 92.0, 0.5, 0.11)
