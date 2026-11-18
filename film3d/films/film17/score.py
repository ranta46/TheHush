def score(S, dur):
    S.add(S.wind(dur, 0.6), 0, 0.22)                                                             # sea wind all film
    S.train_rhythm(0.0, 44.6, 0.28, 0.15)                                                        # already running hard
    for k in range(4): S.add(S.clack(), 0.2 + k * 0.5, 0.2, -0.3)                                # the coast lamps die
    S.add(S.drone(20.0, 38), 0.4, 0.5)
    S.add(S.shh(2.0), 2.8, 0.5); S.add(S.stinger(), 3.4, 0.6)                                    # its face over the dunes
    S.add(S.whistle(1.4), 3.6, 0.8)
    S.chase(4.0, 33.0, bpm=164, gain=0.14)
    S.steps(5.0, 56.0, 0.85, 0.55)                                                               # it walks after us
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 17.0, 0.42, 0.08)    # THEME once, soft: the plan
    for k in range(6): S.add(S.shh(1.8), 33.6 + k * 1.9, 0.18, -0.4 + k * 0.15)                  # the sea over the rails
    S.add(S.drone(14.0, 36), 34.0, 0.4)
    S.add(S.thump(), 44.6, 0.55); S.add(S.stinger(), 44.8, 0.55)                                 # it eats our lamp
    S.silence_music(44.6, 64.6, 0.9)
    for k in range(13): S.add(S.heartbeat(), 46.6 + k * 0.72, 0.45 if k < 5 else 0.6)
    S.add(S.shh(2.4), 49.8, 0.5)
    S.add(S.wind(5.0, 1.6), 55.0, 0.55); S.add(S.shh(3.0), 56.2, 0.7); S.add(S.thump(), 57.2, 0.6)   # the big wave
    S.add(S.drone(6.0, 33), 58.4, 0.45)
    S.add(S.whistle(1.8), 64.6, 0.85)                                                            # fire lit, full steam
    S.train_rhythm(64.6, 89.0, 0.26, 0.15); S.chase(65.0, 80.0, bpm=168, gain=0.14)
    S.steps(66.0, 77.0, 1.1, 0.4)                                                                # it wades after us
    S.add(S.whistle(1.2), 85.5, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 87.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 92.8, 0.5, 0.11)
