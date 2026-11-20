def score(S, dur):
    S.add(S.wind(dur, 0.6), 0, 0.2)                                                              # moor wind all film
    S.train_rhythm(0.0, 41.6, 0.28, 0.15)                                                        # already running hard
    for k in range(3): S.add(S.clack(), 0.2 + k * 0.5, 0.2, -0.3)                                # the moor lamps die
    S.add(S.drone(20.0, 38), 0.4, 0.5)
    S.add(S.shh(2.0), 2.8, 0.5); S.add(S.stinger(), 3.4, 0.6)                                    # its face on the moor
    S.add(S.whistle(1.4), 3.6, 0.8)
    S.chase(4.0, 24.0, bpm=164, gain=0.14)
    S.steps(5.0, 24.2, 0.85, 0.55)                                                               # it walks after us
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 16.2, 0.42, 0.08)    # THEME once, soft: the plan
    S.add(S.thump(), 24.2, 0.6); S.add(S.thump(), 25.0, 0.45)                                    # it stops at the walls
    S.add(S.drone(14.0, 36), 26.0, 0.35)
    S.steps(28.4, 44.0, 1.1, 0.4)                                                                # it walks on the rim
    S.add(S.thump(), 31.6, 0.3); S.add(S.thump(), 36.0, 0.3)                                     # it eats the gorge lamps
    S.add(S.thump(), 42.4, 0.45)                                                                  # it eats the Bowl lamp
    S.silence_music(41.4, 61.2, 0.9)
    for k in range(18): S.add(S.heartbeat(), 43.0 + k * 0.72, 0.45 if k < 6 else 0.6)
    S.add(S.shh(2.4), 46.0, 0.5)
    S.add(S.shh(1.6), 58.6, 0.95, 0.2)                                                           # the drop: HISS on the hot boiler
    S.add(S.stinger(), 59.2, 0.55)
    S.add(S.whistle(1.8), 61.2, 0.85)                                                            # full steam
    S.train_rhythm(61.2, 82.6, 0.26, 0.15); S.chase(61.4, 74.0, bpm=168, gain=0.14)
    S.steps(62.0, 78.4, 0.9, 0.5)
    S.add(S.thump(), 78.4, 0.45)                                                                  # it stops at the cliff edge
    S.add(S.whistle(1.2), 80.6, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 82.8, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 90.4, 0.5, 0.11)
