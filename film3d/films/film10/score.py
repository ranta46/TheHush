def score(S, dur):
    S.add(S.bell(81), 0.0, 0.25); S.add(S.bell(74), 0.35, 0.2); S.add(S.wind(dur, 0.7), 0, 0.22)    # night wind on the moor
    S.train_rhythm(0.0, 29.5, 0.42, 0.14)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 3.6, 0.38, 0.12)     # THEME once
    for k in range(5): S.add(S.clack(), 6.0 + k * 0.5, 0.18, 0.5)                                # the field lamps die
    S.add(S.drone(14.0, 38), 6.5, 0.5)
    S.add(S.shh(2.0), 7.4, 0.5); S.add(S.stinger(), 8.4, 0.55)                                   # it rises behind us
    S.add(S.whistle(1.4), 10.4, 0.8)
    S.train_rhythm(10.4, 28.5, 0.28, 0.15); S.chase(10.6, 28.5, bpm=160, gain=0.14)
    S.steps(9.4, 38.5, 0.8, 0.55)                                                                # it runs after us
    for k in range(4): S.add(S.clack(), 28.4 + k * 0.4, 0.45)                                   # brakes, onto the lift
    S.add(S.thump(), 30.5, 0.6)                                                                  # the lift takes the weight
    S.add(S.clack(), 31.6, 0.6, -0.3)                                                            # the lever
    S.add(S.drone(9.0, 45), 32.0, 0.3)                                                           # the old winch hums
    S.steps(38.5, 47.5, 1.2, 0.5)                                                                # it comes to the foot
    for k in range(6): S.add(S.clack(), 39.0 + k * 0.32, 0.2, -0.4)                             # the incline lamps die
    S.add(S.thump(), 41.0, 0.55)                                                                 # the lift stops
    S.add(S.thump(), 43.6, 0.5)                                                                  # our lights out
    S.silence_music(41.0, 61.5, 0.95)
    S.add(S.drone(20.0, 33), 43.8, 0.5)
    for k in range(18): S.add(S.heartbeat(), 47.0 + k * 0.72, 0.45 if k < 7 else 0.6)
    S.add(S.shh(2.4), 48.0, 0.5); S.add(S.shh(2.4), 53.5, 0.45)
    S.add(S.thump(), 61.5, 0.8); S.add(S.clack(), 61.6, 0.6, 0.3)                               # the old weight slips
    S.add(S.drone(4.0, 50), 61.6, 0.45)
    S.add(S.thump(), 65.4, 0.85)                                                                 # the weight hits the foot / the lift at the top
    S.add(S.stinger(), 64.4, 0.6)                                                                # it turns to us
    S.add(S.whistle(1.8), 66.4, 0.85)
    S.train_rhythm(66.8, 98.0, 0.26, 0.15); S.chase(67.5, 86.0, bpm=168, gain=0.14)
    S.steps(64.0, 90.0, 1.0, 0.4)                                                                # it walks along the foot
    S.add(S.whistle(1.2), 89.5, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 91.0, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 95.0, 0.5, 0.11)
