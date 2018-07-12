![Logo](tabsynthe.png)

A Python-based utility to consume a guitar tab and output a MIDI-style WAV using predefined samples.

# Requirements
* `pip install pydub`
* `pip install pygogo`
* `pip install future`
* Not supported yet, but install ffmpeg / avconv to export to non-WAV format(s).

# TODO
* Some sort of preliminary linter to make sure the tab data isn't complete garbage?
* No exceptions yet, so we're kind of working on the honor system.
* Only exports to WAV right now. :(

# Sample Input
```
python tabsynthe.py -t tabs/tab1.txt -i bass -b 220 -c stereo
```

# Sample Output
```
2018-07-12 13:16:38,716 - INFO - BPM: 220
2018-07-12 13:16:38,717 - INFO - Slice (in ms): 272
2018-07-12 13:16:38,719 - INFO - Root: f1
2018-07-12 13:16:38,719 - INFO - Notes to play: ['-', '-', '-', '1', '2', '-', '-', '-', '-', '0', '-']
2018-07-12 13:16:38,719 - INFO - Root: c1
2018-07-12 13:16:38,720 - INFO - Notes to play: ['-', '-', '-', '-', '-', '-', '-', '-', '7', '-', '-']
2018-07-12 13:16:38,720 - INFO - Root: g0
2018-07-12 13:16:38,720 - INFO - Notes to play: ['-', '-', '-', '-', '-', '-', '-', '5', '-', '2', '-']
2018-07-12 13:16:38,721 - INFO - Root: c0
2018-07-12 13:16:38,721 - INFO - Notes to play: ['-', '0', '-', '8', '-', '-', '0', '-', '-', '-', '-']
2018-07-12 13:16:38,723 - DEBUG - Silence detected.
2018-07-12 13:16:38,723 - DEBUG - Notes for segment 1: ['c0']
2018-07-12 13:16:38,875 - DEBUG - Silence detected.
2018-07-12 13:16:38,877 - DEBUG - Notes for segment 3: ['f2', 'gs0']
2018-07-12 13:16:39,151 - DEBUG - Silence detected.
2018-07-12 13:16:39,151 - DEBUG - Notes for segment 6: ['c0']
2018-07-12 13:16:39,305 - DEBUG - Notes for segment 7: ['c1']
2018-07-12 13:16:39,457 - DEBUG - Notes for segment 8: ['g1']
2018-07-12 13:16:39,582 - DEBUG - Notes for segment 9: ['f1', 'a0']
2018-07-12 13:16:39,868 - DEBUG - Silence detected.
```
