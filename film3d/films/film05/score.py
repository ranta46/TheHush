def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 0.8), 0, 0.25)   # night wind over the lake
    S.train_rhythm(0.0, 26.0, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 4.5, 0.38, 0.12)   # THEME once
    for k in range(6): S.add(S.clack(), 9.3 + k * 0.25, 0.2, 0.5)                               # the mill windows die
    S.add(S.drone(14.0, 38), 9.6, 0.5)
    S.add(S.shh(2.0), 14.0, 0.5); S.add(S.stinger(), 16.2, 0.55)                               # it rises behind the hills
    S.add(S.whistle(1.4), 25.8, 0.75)
    S.train_rhythm(25.8, 49.5, 0.24, 0.16); S.chase(26.0, 49.0, bpm=164, gain=0.15)
    S.steps(18.5, 53.0, 0.8, 0.55)
    for k in range(3): S.add(S.clack(), 49.6 + k * 0.35, 0.6)                                  # brakes
    S.add(S.thump(), 51.0, 0.6); S.add(S.drone(4.5, 30), 51.2, 0.45)                           # lever, the bridge goes up
    S.add(S.thump(), 55.0, 0.7)
    for k in range(4): S.add(S.clack(), 56.8 + k * 0.4, 0.35, -0.3)                            # our lights die
    S.silence_music(56.8, 78.5, 0.95)
    S.add(S.drone(20.0, 33), 57.5, 0.7)
    for k in range(13): S.add(S.heartbeat(), 62.0 + k * 0.78, 0.5 if k < 6 else 0.6)
    S.add(S.shh(2.4), 63.0, 0.5); S.add(S.shh(2.4), 69.0, 0.45)
    for t, g in ((72.5, 0.6), (74.0, 0.65), (75.5, 0.7)): S.add(S.thump(), t, g); S.add(S.clack(), t + 0.05, 0.5)   # chains slip
    S.add(S.thump(), 77.9, 0.9); S.add(S.clack(), 78.0, 0.7)                                    # the bridge is down
    S.add(S.whistle(1.8), 78.4, 0.85)
    S.train_rhythm(78.4, dur - 0.5, 0.26, 0.15); S.chase(79.0, 86.5, bpm=168, gain=0.14)
    S.steps(82.0, 92.0, 1.0, 0.45)                                                              # it walks over the bridge
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 87.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 92.0, 0.5, 0.11)
