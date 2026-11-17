def score(S, dur):
    S.add(S.wind(dur, 0.5), 0, 0.2)
    S.train_rhythm(0.0, 21.2, 0.28, 0.15)                                                        # already running hard
    for k in range(4): S.add(S.clack(), 0.2 + k * 0.5, 0.2, -0.3)                                # the lamps behind die
    S.add(S.drone(20.0, 38), 0.4, 0.5)
    S.add(S.shh(2.0), 2.8, 0.5); S.add(S.stinger(), 3.4, 0.6)                                    # its face over the ridge, the moon
    S.add(S.whistle(1.4), 3.6, 0.8)
    S.chase(4.0, 21.2, bpm=164, gain=0.14)
    S.steps(5.0, 42.0, 0.8, 0.55)                                                                # it walks over the flat
    S.add(S.thump(), 21.2, 0.5)                                                                  # our lights out, into its shadow
    S.silence_music(21.2, 60.0, 0.9)
    S.add(S.drone(18.0, 36), 21.8, 0.4)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 31.0, 0.42, 0.08)    # THEME once, soft: the plan
    S.add(S.drone(12.0, 33), 41.4, 0.5)                                                          # it stops
    for k in range(13): S.add(S.heartbeat(), 44.6 + k * 0.75, 0.45 if k < 5 else 0.6)
    S.add(S.shh(2.4), 49.8, 0.5); S.add(S.shh(2.4), 53.0, 0.45)
    for k in range(3): S.add(S.clack(), 55.0 + k * 0.3, 0.15, 0.4)                               # the old lamp flickers on by itself
    S.add(S.stinger(), 55.6, 0.5); S.steps(55.8, 58.4, 0.9, 0.6)                                 # it steps aside
    S.add(S.thump(), 59.2, 0.55); S.add(S.stinger(), 59.4, 0.6)                                  # it sees us
    S.add(S.whistle(1.8), 60.2, 0.85)
    S.train_rhythm(60.2, 95.0, 0.26, 0.15); S.chase(60.6, 86.0, bpm=168, gain=0.14)
    S.steps(60.0, 95.0, 1.0, 0.4)
    S.add(S.whistle(1.2), 87.5, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 89.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 94.0, 0.5, 0.11)
