def score(S, dur):
    S.add(S.wind(dur, 0.5), 0, 0.2)                                                              # moor wind all film
    S.train_rhythm(0.0, 22.0, 0.28, 0.15)                                                        # already running hard
    for k in range(3): S.add(S.clack(), 0.2 + k * 0.5, 0.2, -0.3)                                # the moor lamps die
    S.add(S.drone(10.0, 38), 0.4, 0.5)
    S.add(S.shh(2.0), 2.8, 0.5); S.add(S.stinger(), 3.4, 0.6)                                    # its face rises
    S.chase(4.0, 21.8, bpm=166, gain=0.14)
    S.steps(4.4, 44.6, 0.85, 0.55)                                                               # it walks after us
    S.add(S.stinger(), 7.9, 0.7); S.add(S.thump(), 8.0, 0.6)                                     # it is at the last car
    S.add(S.whistle(1.4), 10.4, 0.8)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 12.8, 0.42, 0.08)    # THEME once, soft
    S.silence_music(22.0, 62.6, 0.9)                                                             # lights out: into the fog
    S.train_rhythm(22.0, 42.4, 0.6, 0.06)                                                        # creeping, very soft
    S.add(S.drone(40.0, 33), 22.4, 0.45)
    S.add(S.shh(1.8), 26.0, 0.4)                                                                 # it looks over the white
    for k in range(16): S.add(S.heartbeat(), 41.6 + k * 0.7, 0.45 if k < 5 else 0.6)
    S.add(S.shh(2.4), 45.2, 0.5); S.add(S.stinger(), 46.6, 0.45)                                 # its face comes down to the fog
    S.add(S.drone(3.0, 45), 50.5, 0.35)                                                          # the fog rises
    S.add(S.shh(2.0), 54.4, 0.4)
    S.train_rhythm(56.6, 62.6, 0.45, 0.07)                                                       # we creep out
    S.add(S.whistle(1.8), 62.8, 0.85)
    S.train_rhythm(62.8, 84.6, 0.26, 0.15); S.chase(63.0, 76.0, bpm=168, gain=0.14)
    S.steps(64.8, 86.0, 0.95, 0.45)
    S.add(S.whistle(1.2), 82.6, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 84.8, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 88.4, 0.5, 0.11)
