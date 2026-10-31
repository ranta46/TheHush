def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur), 0, 0.3)
    S.train_rhythm(0.0, 24.0, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 4.5, 0.38, 0.12)   # THEME once
    S.add(S.drone(14.0, 38), 15.0, 0.5)
    for k in range(10): S.add(S.clack(), 25.0 + k * 0.75, 0.25, -0.4)                          # lamps dying
    S.add(S.shh(2.0), 26.0, 0.5); S.add(S.stinger(), 28.5, 0.55)                               # its eyes open
    S.add(S.whistle(1.4), 32.0, 0.75)
    S.train_rhythm(32.0, 47.0, 0.24, 0.16); S.chase(32.2, 47.0, bpm=160, gain=0.14)
    S.steps(30.0, 46.0, 0.8, 0.5)
    S.add(S.clack(), 44.0, 0.9); S.add(S.clack(), 44.2, 0.8)
    S.silence_music(48.0, 76.0, 0.95)
    S.add(S.drone(26.0, 33), 49.0, 0.8)
    for k in range(20): S.add(S.heartbeat(), 54.5 + k * 1.0, 0.5 if k < 10 else 0.6)
    S.add(S.shh(2.4), 58.0, 0.5); S.add(S.shh(2.4), 66.0, 0.45)
    S.add(S.steps(74.0, 80.0, 1.1, 0.4) or S.thump(), 74.0, 0.3)
    S.add(S.whistle(1.8), 77.6, 0.9)
    S.train_rhythm(78.0, dur - 0.5, 0.26, 0.15); S.chase(78.2, 86.0, bpm=168, gain=0.15)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 86.6, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 92.0, 0.5, 0.11)
