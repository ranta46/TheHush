def score(S, dur):
    S.add(S.wind(dur, 0.5), 0, 0.2)                                                              # night wind all film
    S.train_rhythm(0.0, 25.4, 0.28, 0.15)                                                        # already running hard
    for k in range(3): S.add(S.clack(), 0.2 + k * 0.5, 0.2, -0.3)                                # the yard lamps die
    S.add(S.drone(10.0, 38), 0.4, 0.5)
    S.add(S.shh(2.0), 2.8, 0.5); S.add(S.stinger(), 3.4, 0.6)                                    # its face rises
    S.chase(4.0, 22.6, bpm=166, gain=0.14)
    S.steps(4.4, 22.6, 0.8, 0.6)                                                                 # it walks after us
    S.add(S.stinger(), 7.9, 0.7); S.add(S.thump(), 8.0, 0.6)                                     # it is at the last car
    S.add(S.whistle(1.4), 10.4, 0.8)                                                             # full steam
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 16.8, 0.42, 0.08)    # THEME once, soft: the plan
    S.add(S.thump(), 23.6, 0.5); S.add(S.thump(), 24.0, 0.55)                                    # the doors close
    S.silence_music(25.6, 62.0, 0.9)
    S.add(S.drone(30.0, 33), 26.0, 0.45)
    S.steps(26.0, 42.0, 1.1, 0.45)                                                               # it comes to the shed
    S.add(S.thump(), 28.5, 0.35); S.add(S.thump(), 41.1, 0.35)                                   # it eats the shed lamps
    for k in range(20): S.add(S.heartbeat(), 40.0 + k * 0.72, 0.45 if k < 6 else 0.6)
    S.add(S.shh(2.4), 43.0, 0.5)
    S.steps(53.5, 57.8, 1.0, 0.6)                                                                # it goes, heavy steps
    S.add(S.clack(), 57.5, 0.3, 0.2); S.add(S.clack(), 57.8, 0.35, 0.2)                          # the loose pane rattles
    S.add(S.clack(), 58.85, 0.95, 0.2); S.add(S.clack(), 58.9, 0.8, -0.2); S.add(S.clack(), 59.0, 0.6, 0.1)   # CRASH: the glass breaks
    S.add(S.stinger(), 59.3, 0.6)
    S.add(S.thump(), 62.4, 0.7); S.add(S.thump(), 62.6, 0.6)                                     # the back doors burst open
    S.add(S.whistle(1.8), 62.0, 0.85)
    S.train_rhythm(62.2, 84.6, 0.26, 0.15); S.chase(62.4, 76.0, bpm=168, gain=0.14)
    S.steps(63.0, 86.0, 0.95, 0.5)
    S.add(S.whistle(1.2), 82.6, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 84.8, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 90.4, 0.5, 0.11)
