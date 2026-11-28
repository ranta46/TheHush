def score(S, dur):
    S.add(S.wind(dur, 0.5), 0, 0.22)                                                             # lake wind all film (same at start and end = loop)
    S.add(S.drone(13.2, 36), 0, 0.42)                                                            # low hum of the hill
    S.train_rhythm(0.0, 13.4, 0.5, 0.08)                                                         # creeping, soft
    S.add(S.shh(1.6), 0.2, 0.35)
    for k in range(4): S.add(S.clack(), 3.8 + k * 0.7, 0.2, -0.3 + k * 0.2)                      # the lamps die near it
    S.add(S.heartbeat(), 9.0, 0.5); S.add(S.shh(1.4), 9.4, 0.45)                                 # its eyes flare
    for k in range(5): S.add(S.heartbeat(), 11.0 + k * 0.45, 0.55)
    S.add(S.stinger(), 13.35, 1.0); S.add(S.thump(), 13.4, 0.9)                                  # THE sting: the hill stands up
    S.steps(14.6, 19.0, 0.8, 0.7)
    S.add(S.whistle(1.3), 14.0, 0.8)
    S.train_rhythm(13.8, 18.8, 0.26, 0.16); S.chase(14.0, 18.8, bpm=170, gain=0.15)
    S.silence_music(18.8, 22.4, 0.95)
    S.add(S.shh(2.4), 19.0, 0.55)
    for k in range(5): S.add(S.heartbeat(), 19.4 + k * 0.6, 0.6)
    S.train_rhythm(22.4, dur, 0.5, 0.08)                                                         # creeping again
    S.add(S.drone(dur - 22.6, 36), 22.6, 0.42)
    S.add(S.shh(1.4), dur - 1.2, 0.35)                                                           # leads back into the first second
