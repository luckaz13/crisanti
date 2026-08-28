# Vlak video start time

## Objective

Start the video in the first slide of the “Vlak: O jogo do trem” gallery at
00:10 in both PT-BR and Spanish versions. After the initial seek, leaving and
returning to the slide must resume playback from the paused position.

## Design

Both Vlak video elements will declare `data-start-time="10"`. The shared
gallery controller will read that value after video metadata becomes available,
seek once to the requested second, and record that the initial seek has been
applied. Existing visibility and slide-navigation logic will remain responsible
for play and pause, so later visits to the slide do not seek again.

If the declared value is absent, invalid, negative, or beyond the media
duration, the controller will leave the playback position unchanged. This keeps
the behavior safe for any future gallery videos that do not opt in.

## Verification

- Assert that PT-BR and Spanish markup declare a 10-second start time.
- Assert that the controller applies the configured start time once after
  metadata is available.
- Assert that ordinary pause/resume navigation does not reapply the seek.
- Run the complete test suite and validate the behavior in a browser.
