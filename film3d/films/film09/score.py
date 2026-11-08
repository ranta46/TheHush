def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 0.7), 0, 0.2)    # night wind in the valley
    S.train_rhythm(0.0, 29.0, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 3.8, 0.38, 0.12)     # THEME once
    for k in range(5): S.add(S.clack(), 8.0 + k * 0.5, 0.18, -0.5)                               # the road lamps die
    S.add(S.drone(14.0, 38), 8.5, 0.5)
    S.add(S.shh(2.0), 9.6, 0.5); S.add(S.stinger(), 10.6, 0.55)                                  # it rises behind us
    S.add(S.whistle(1.4), 15.8, 0.8)
    S.train_rhythm(15.8, 28.5, 0.28, 0.15); S.chase(16.0, 28.5, bpm=160, gain=0.14)
    S.steps(11.5, 35.0, 0.8, 0.55)                                                               # it runs after us
    for k in range(4): S.add(S.clack(), 28.6 + k * 0.4, 0.45)                                   # brakes, onto the ferry
    S.add(S.thump(), 31.0, 0.6)                                                                  # the ferry takes the weight
    S.add(S.clack(), 33.0, 0.6, -0.3)                                                            # the rope snaps
    S.add(S.thump(), 35.4, 0.5)                                                                  # our lights out
    S.silence_music(35.4, 63.5, 0.95)
    S.add(S.drone(28.0, 33), 35.6, 0.5)
    S.steps(35.0, 42.0, 1.1, 0.45)                                                               # it comes to the bank
    S.add(S.clack(), 39.0, 0.2, -0.4)                                                            # the dock lamp dies
    S.steps(42.0, 47.0, 1.3, 0.5)                                                                # it wades in
    for k in range(20): S.add(S.heartbeat(), 46.0 + k * 0.72, 0.45 if k < 8 else 0.6)
    S.add(S.shh(2.4), 47.5, 0.5); S.add(S.shh(2.4), 53.0, 0.45)
    S.steps(55.5, 63.0, 1.5, 0.35)
    S.add(S.thump(), 63.6, 0.75)                                                                 # the ferry bumps the far dock
    for i, t in enumerate((63.7, 64.2, 64.7, 65.3, 65.9)): S.add(S.bell(86 - (i % 2) * 3, 1.6), t, 0.4 - i * 0.05, 0.4)   # the old dock bell
    S.add(S.stinger(), 64.4, 0.6)                                                                # it turns to us
    S.add(S.whistle(1.8), 66.5, 0.85)
    S.train_rhythm(66.8, 98.0, 0.26, 0.15); S.chase(67.5, 88.0, bpm=168, gain=0.14)
    S.steps(66.0, 92.0, 0.8, 0.5)                                                                # it wades after us
    S.add(S.whistle(1.2), 89.5, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 91.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 95.0, 0.5, 0.11)
