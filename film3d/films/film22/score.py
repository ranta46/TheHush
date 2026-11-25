def score(S, dur):
    S.add(S.wind(dur, 0.7), 0, 0.22)                                                             # storm wind all film
    S.train_rhythm(0.0, 23.0, 0.28, 0.15)                                                        # already running hard
    for k in range(3): S.add(S.clack(), 0.2 + k * 0.5, 0.2, -0.3)                                # the heath lamps die
    S.add(S.drone(10.0, 38), 0.4, 0.5)
    S.add(S.shh(2.0), 2.8, 0.5); S.add(S.stinger(), 3.4, 0.6)                                    # its face rises
    S.chase(4.0, 22.4, bpm=166, gain=0.14)
    S.steps(4.4, 45.0, 0.8, 0.6)                                                                 # it walks after us
    S.add(S.stinger(), 7.9, 0.7); S.add(S.thump(), 8.0, 0.6)                                     # it is at the last car
    S.add(S.whistle(1.4), 10.4, 0.8)
    S.play([(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)], 12.8, 0.42, 0.08)    # THEME once, soft
    def thunder(t, g):                                                                           # thunder = low thump + rumble
        S.add(S.thump(), t, g); S.add(S.thump(), t + 0.25, g * 0.7); S.add(S.drone(2.2, 28), t + 0.1, g * 0.6)
    thunder(18.4, 0.35)                                                                          # the far flash
    for t in (20.0, 26.5, 31.0, 35.5, 40.0): thunder(t + 0.2, 0.75)
    S.add(S.shh(1.6), 20.6, 0.45)                                                                # it eats the light
    S.silence_music(23.4, 59.6, 0.9)
    S.add(S.drone(36.0, 33), 23.6, 0.45)
    for t in (26.5, 31.0, 35.5, 40.0, 52.8): S.train_rhythm(t, t + 1.9, 0.32, 0.12)              # we move only in the flashes
    for k in range(18): S.add(S.heartbeat(), 41.6 + k * 0.7, 0.45 if k < 6 else 0.6)
    S.add(S.shh(2.4), 44.6, 0.5)
    thunder(53.0, 0.6)
    thunder(56.6, 1.0); S.add(S.stinger(), 56.7, 0.7)                                            # it hits the old signal
    S.add(S.shh(2.0), 58.2, 0.45)
    S.add(S.whistle(1.8), 59.8, 0.85)
    S.train_rhythm(60.0, 84.6, 0.26, 0.15); S.chase(60.2, 76.0, bpm=168, gain=0.14)
    S.steps(66.0, 86.0, 0.95, 0.45)
    thunder(66.2, 0.25); thunder(75.2, 0.18)                                                     # the storm goes away
    S.add(S.whistle(1.2), 82.6, 0.6)
    S.play([(74, 1), (78, 1), (81, 1), (86, 2)], 84.8, 0.32, 0.13)
    S.play([(74, 1), (77, 1), (81, 2)], 88.4, 0.5, 0.11)
