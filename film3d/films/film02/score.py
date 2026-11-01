def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur), 0, 0.35)
    S.train_rhythm(0.0, 24.0, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 4.5, 0.38, 0.12)   # THEME once
    for k in range(5): S.add(S.clack(), 14.4 + k * 0.35, 0.22, 0.3)                             # hill lamps die
    S.add(S.drone(12.0, 38), 15.0, 0.5)
    S.add(S.shh(2.0), 26.0, 0.5); S.add(S.stinger(), 28.5, 0.55)                               # its eyes open
    S.add(S.whistle(1.4), 32.0, 0.75)
    S.train_rhythm(32.0, 45.0, 0.24, 0.16); S.chase(32.2, 52.0, bpm=160, gain=0.14)
    S.steps(30.0, 50.0, 0.8, 0.5)
    S.add(S.clack(), 44.6, 0.9); S.add(S.thump(), 45.0, 0.5)                                   # unhook
    S.train_rhythm(45.0, 52.0, 0.22, 0.15)
    S.add(S.shh(2.4), 52.0, 0.5)                                                                # it eats the lantern
    S.silence_music(53.0, 74.5, 0.95)
    S.add(S.drone(21.0, 33), 53.5, 0.8)
    S.steps(58.0, 70.5, 1.2, 0.45)
    for k in range(14): S.add(S.heartbeat(), 61.0 + k * 0.7, 0.5 if k < 7 else 0.6)
    S.add(S.shh(2.4), 66.5, 0.45)
    S.add(S.stinger(), 70.8, 0.5); S.add(S.thump(), 71.0, 0.7); S.add(S.thump(), 72.0, 0.6)     # the ice breaks
    S.add(S.whistle(1.8), 74.8, 0.9)
    S.train_rhythm(75.0, dur - 0.5, 0.26, 0.15); S.chase(75.2, 85.0, bpm=168, gain=0.15)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 85.5, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 92.0, 0.5, 0.11)
