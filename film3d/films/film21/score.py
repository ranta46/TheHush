def score(S, dur):
    S.add(S.wind(dur, 0.5), 0, 0.2)                                                              # night wind all film
    S.train_rhythm(0.0, 23.0, 0.28, 0.15)                                                        # already running hard
    for k in range(3): S.add(S.clack(), 0.2 + k * 0.5, 0.2, -0.3)                                # the valley lamps die
    S.add(S.drone(10.0, 38), 0.4, 0.5)
    S.add(S.shh(2.0), 2.8, 0.5); S.add(S.stinger(), 3.4, 0.6)                                    # its face rises
    S.chase(4.0, 22.4, bpm=166, gain=0.14)
    S.steps(4.4, 31.0, 0.8, 0.6)                                                                 # it walks after us
    S.add(S.stinger(), 7.9, 0.7); S.add(S.thump(), 8.0, 0.6)                                     # it is at the last car
    S.add(S.whistle(1.4), 10.4, 0.8)                                                             # full steam
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 16.8, 0.42, 0.08)    # THEME once, soft: the plan
    S.silence_music(23.4, 59.6, 0.9)
    S.add(S.drone(36.0, 33), 23.6, 0.45)
    S.add(S.thump(), 29.4, 0.35)                                                                 # it eats the door lamp
    S.add(S.shh(2.4), 31.8, 0.5); S.add(S.stinger(), 32.2, 0.45)                                 # its face fills the door
    for k in range(24): S.add(S.heartbeat(), 40.0 + k * 0.7, 0.45 if k < 8 else 0.6)
    S.add(S.shh(2.4), 44.6, 0.5)
    S.add(S.clack(), 56.0, 0.3, 0.2)                                                             # the wheel knocks the stone
    S.add(S.clack(), 56.95, 0.6, -0.2); S.add(S.clack(), 57.3, 0.9, 0.0); S.add(S.clack(), 57.5, 0.5, 0.1)   # clack, clack on the rails
    S.add(S.stinger(), 58.0, 0.65)                                                               # it looks up
    S.add(S.whistle(1.8), 59.8, 0.85)
    S.train_rhythm(60.0, 84.6, 0.26, 0.15); S.chase(60.2, 76.0, bpm=168, gain=0.14)
    S.steps(60.4, 86.0, 0.95, 0.5)
    S.add(S.whistle(1.2), 82.6, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 84.8, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 88.4, 0.5, 0.11)
