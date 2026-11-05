def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 0.8), 0, 0.25)   # wind over the windmill hills
    S.train_rhythm(0.0, 20.2, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 4.5, 0.38, 0.12)   # THEME once
    for k in range(9): S.add(S.clack(), 8.5 + k * 0.45, 0.18, 0.5)                              # the windmill lamps die, far ones first
    S.add(S.drone(12.0, 38), 9.0, 0.5)
    S.add(S.shh(2.0), 14.5, 0.5); S.add(S.stinger(), 16.6, 0.55)                               # it rises ahead, on the line
    for k in range(3): S.add(S.clack(), 20.0 + k * 0.35, 0.6)                                  # brakes
    S.add(S.whistle(1.4), 21.2, 0.75)
    S.train_rhythm(22.0, 43.5, 0.26, 0.16); S.chase(22.5, 43.0, bpm=164, gain=0.15)            # running backwards
    S.steps(19.0, 54.0, 0.8, 0.55)
    for k in range(3): S.add(S.clack(), 43.2 + k * 0.35, 0.55)
    S.add(S.thump(), 44.6, 0.6); S.add(S.drone(21.0, 30), 45.0, 0.35)                          # the table starts to turn
    for k in range(10): S.add(S.clack(), 46.0 + k * 2.0, 0.22, -0.2)                            # creak... creak...
    for k in range(5): S.add(S.clack(), 50.5 + k * 0.45, 0.35, 0.3)                             # yard lamps die
    for k in range(4): S.add(S.clack(), 53.8 + k * 0.4, 0.35, -0.3)                             # our lights die
    S.silence_music(53.8, 76.4, 0.95)
    S.add(S.drone(20.0, 33), 55.0, 0.7)
    for k in range(14): S.add(S.heartbeat(), 56.5 + k * 0.78, 0.5 if k < 7 else 0.6)
    S.add(S.shh(2.4), 58.0, 0.5); S.add(S.shh(2.4), 65.0, 0.45)
    S.add(S.thump(), 66.0, 0.7)                                                                 # the table locks in line
    S.add(S.wind(7.0, 1.0), 68.5, 0.6)                                                          # the gust
    for t in (70.0, 71.0, 71.8, 72.5, 73.2, 73.9): S.add(S.thump(), t, 0.45)                    # the sails sweep round
    S.add(S.whistle(1.8), 76.3, 0.85)
    S.train_rhythm(76.5, dur - 0.5, 0.26, 0.15); S.chase(77.0, 85.0, bpm=168, gain=0.14)
    S.steps(79.0, 96.0, 1.0, 0.45)                                                              # it follows up the branch line
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 86.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 92.0, 0.5, 0.11)
