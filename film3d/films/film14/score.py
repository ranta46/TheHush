def score(S, dur):
    S.add(S.wind(dur, 0.5), 0, 0.2)
    S.train_rhythm(0.0, 22.0, 0.28, 0.15)                                                        # already running hard
    for k in range(4): S.add(S.clack(), 0.2 + k * 0.55, 0.2, -0.3)                               # the lamps behind die
    S.add(S.drone(20.0, 38), 0.4, 0.5)
    S.add(S.shh(2.0), 2.8, 0.5); S.add(S.stinger(), 3.4, 0.6)                                    # its face over the ridge
    S.add(S.whistle(1.4), 3.6, 0.8)
    S.chase(4.0, 21.0, bpm=164, gain=0.14)
    S.steps(5.0, 46.0, 0.8, 0.55)                                                                # it comes over the meadow
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 24.4, 0.42, 0.12)    # THEME once: the lanterns light up
    for k in range(8): S.add(S.bell(86 + (k % 3) * 3, 1.5), 26.0 + k * 0.6, 0.06, -0.4 + k * 0.1)  # little bells as they go up
    S.add(S.thump(), 30.8, 0.5)                                                                  # our lights out
    S.silence_music(30.8, 60.0, 0.9)
    S.add(S.drone(16.0, 36), 31.4, 0.4)
    S.add(S.drone(10.0, 33), 45.4, 0.5)
    for k in range(13): S.add(S.heartbeat(), 46.4 + k * 0.7, 0.45 if k < 5 else 0.6)
    S.add(S.shh(2.4), 49.8, 0.5); S.add(S.shh(2.4), 53.0, 0.45)
    S.add(S.stinger(), 55.5, 0.6)                                                                # the lantern lands on our stack
    S.add(S.thump(), 56.2, 0.5)                                                                  # it looks down at us
    S.add(S.whistle(1.8), 60.2, 0.85)
    S.train_rhythm(60.2, 95.0, 0.26, 0.15); S.chase(60.6, 86.0, bpm=168, gain=0.14)
    S.steps(60.0, 95.0, 1.0, 0.4)
    S.add(S.whistle(1.2), 87.5, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 89.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 94.0, 0.5, 0.11)
