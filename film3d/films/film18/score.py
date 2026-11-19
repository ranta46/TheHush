def score(S, dur):
    S.add(S.wind(dur, 0.6), 0, 0.2)                                                              # mountain wind all film
    S.train_rhythm(0.0, 28.0, 0.28, 0.15)                                                        # already running hard
    for k in range(3): S.add(S.clack(), 0.2 + k * 0.5, 0.2, -0.3)                                # the valley lamps die
    S.add(S.drone(20.0, 38), 0.4, 0.5)
    S.add(S.shh(2.0), 2.8, 0.5); S.add(S.stinger(), 3.4, 0.6)                                    # its face in the valley
    S.add(S.whistle(1.4), 3.6, 0.8)
    S.chase(4.0, 28.0, bpm=164, gain=0.14)
    S.steps(5.0, 41.0, 0.85, 0.55)                                                               # it walks after us
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 16.2, 0.42, 0.08)    # THEME once, soft: the plan
    S.add(S.clack(), 30.2, 0.3); S.add(S.clack(), 31.2, 0.3)                                     # switch one
    S.train_rhythm(31.4, 41.6, 0.3, 0.12)
    S.add(S.shh(2.4), 31.6, 0.5, 0.3); S.add(S.thump(), 32.0, 0.4)                               # the stones slide
    S.add(S.drone(10.0, 36), 34.0, 0.35)
    S.add(S.thump(), 40.9, 0.4)                                                                   # it eats the switch lamp
    S.silence_music(41.4, 63.8, 0.9)
    for k in range(17): S.add(S.heartbeat(), 43.0 + k * 0.72, 0.45 if k < 6 else 0.6)
    S.add(S.shh(2.4), 46.0, 0.5)
    S.add(S.shh(2.0), 54.2, 0.5, 0.3); S.add(S.thump(), 54.6, 0.35)                              # the stones give a little
    S.add(S.clack(), 60.2, 0.4); S.add(S.clack(), 60.8, 0.4); S.add(S.clack(), 61.4, 0.4)        # the wheels slip back
    S.add(S.whistle(1.8), 63.8, 0.85)                                                            # sand, full steam
    S.train_rhythm(63.8, 86.6, 0.26, 0.15); S.chase(64.0, 76.0, bpm=168, gain=0.14)
    S.add(S.shh(3.0), 67.4, 0.6, 0.3); S.add(S.thump(), 68.0, 0.55); S.add(S.thump(), 70.4, 0.5)  # it slides all the way down
    S.add(S.whistle(1.2), 85.0, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 86.8, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 90.4, 0.5, 0.11)
