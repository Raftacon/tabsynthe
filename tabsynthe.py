# REQUIREMENTS:
#     `pip install pydub`
#     `pip install pygogo`
#     `pip install future`
#     Not supported yet, but install ffmpeg / avconv to export to non-WAV format(s).

# TO USE:
# --tab tab.txt (text file name of tab to process)
# --instrument instrument_name (sub-folder name in 'samples' containing instr_samples)
# --bpm 120 (any number)
# --channel-type (mono or stereo supported)
# --name test.wav (or date-time if unspecified)

# TODO:
# Some sort of preliminary linter to make sure the tab data isn't complete garbage?
# No exceptions yet, so we're kind of working on the honor system.
# Only exports to WAV right now. :(
# Need a better way to determine double-digit notes or just really fast subsequent notes on the same line.

import os
import datetime
import argparse
import logging
import pygogo as gogo
from pydub import AudioSegment

absolute_scale = [
	"c0", "cs0", "d0", "ds0", "e0", "f0", "fs0", "g0", "gs0", "a0", "as0", "b0",
	"c1", "cs1", "d1", "ds1", "e1", "f1", "fs1", "g1", "gs1", "a1", "as1", "b1",
	"c2", "cs2", "d2", "ds2", "e2", "f2", "fs2", "g2", "gs2", "a2", "as2", "b2",
	"c3", "cs3", "d3", "ds3"
]

def flat_to_sharp(flat_note):
	note_map = { 'bb': 'as', 'db': 'cs', 'eb': 'ds', 'gb': 'fs', 'ab': 'gs' }
	return note_map[flat_note]

def generate_tone(tab, base_note):
	eligible_tone_list = []

	for note in absolute_scale:
		if note.startswith(base_note):
			# Are we dealing with a sharp?
			if ('s' in note and 's' in base_note) or (not 's' in note and not 's' in base_note): 
				eligible_tone_list.append(note)

	# Pare down eligible list against options already chosen:
	for line in tab.line_list:
		if line.root in eligible_tone_list:
			eligible_tone_list.remove(line.root)

	# Make sure we're only ascending the note tree:
	for note in eligible_tone_list:
		for line in tab.line_list:
			if absolute_scale.index(line.root) > absolute_scale.index(note):
				eligible_tone_list.remove(note)
				break

	# Choose best remaining option:
	return eligible_tone_list[0]

def generate_note_segment(notes, instrument, slice_time):
	individual_segments = []

	for note in notes:
		full_segment = AudioSegment.from_wav("instruments/" + instrument + "/" + note + ".wav")
		individual_segments.append(full_segment[:slice_time]) # Trim full to fit slice time.

	final_segment = individual_segments[0]
	individual_segments.remove(individual_segments[0])

	for segment in individual_segments:
		final_segment = final_segment.overlay(segment)

	return final_segment

def configure_parser(parser):
	parser.add_argument('-t', '--tab', type=str, required=True,
		help='relative path to tab')
	parser.add_argument('-i', '--instrument', type=str, required=True,
		help='subfolder name within "instruments" containing playable note samples')
	parser.add_argument('-b', '--bpm', type=int, required=True,
		help='beats per minute to use when exporting the sample')
	parser.add_argument('-c', '--channel-type', type=str, required=True,
		help='determine whether to take the samples as stereo or mono')
	parser.add_argument('-n', '--name', type=str,
		help='export using this name, else use something auto-generated')

class Line:
	def __init__(self, root, notes_to_play):
		self.root = root
		self.notes_to_play = notes_to_play

class Tab:
	line_list = []

	def __init__(self, tab_filepath):
		base_note = str()
		notes_to_play = []

		# Process root notes first:
		for line in reversed(open(tab_filepath).readlines()):
			chars = list(line.rstrip())
			line_length = len(chars)

			if chars[1] != "|":
				if chars[1] == "b":
					base_note = flat_to_sharp(chars[0].lower() + 'b')
					notes_to_play = chars[3:line_length-1]
				elif chars[1] == "#":
					base_note = chars[0].lower() + 's'
					notes_to_play = chars[3:line_length-1]
			else:
				base_note = chars[0].lower()
				notes_to_play = chars[2:line_length-1]

			tone = generate_tone(self, base_note)
			self.line_list.append(Line(tone, notes_to_play))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Use instrument note samples to generate a WAV from a tab.')
	configure_parser(parser)
	
	args = vars(parser.parse_args())

	# Configure custom logger:
	log_format = '%(asctime)s - %(levelname)s - %(message)s'
	formatter = logging.Formatter(log_format)

	logger = gogo.Gogo(
    	'examples.fmt',
    	low_formatter=formatter,
    	high_formatter=formatter).logger

	tab = Tab(args['tab'])
	bpm = args['bpm']
	slice_time = 60000 / bpm

	logger.info("BPM: " + str(bpm))
	logger.info("Slice (in ms): " + str(slice_time))

	for line in reversed(tab.line_list):
		logger.info("Root: " + line.root)
		logger.info("Notes to play: " + str(line.notes_to_play))

	silence_segment = AudioSegment.silent(duration=slice_time)

	song = AudioSegment.empty() # Assign a dummy to declare type before we append segments.

	skip = False

	for index in range(len(tab.line_list[0].notes_to_play)):
		if not skip == True:
			is_silence = True
			notes = []

			for line in reversed(tab.line_list):
				# Is this a double-digit fret?
				if not line.notes_to_play[index] == '-' and not line.notes_to_play[index+1] == '-':
					is_silence = False
					skip = True # Skip a column to make up the offset in the tab.

					abs_index = absolute_scale.index(line.root) + int(line.notes_to_play[index] + line.notes_to_play[index+1])
					notes.append(absolute_scale[abs_index])
				elif not line.notes_to_play[index] == '-':
					is_silence = False

					abs_index = absolute_scale.index(line.root) + int(line.notes_to_play[index])
					notes.append(absolute_scale[abs_index])

			if is_silence:
				logger.debug("Silence detected.")
				song += silence_segment
			else:
				logger.debug("Notes for segment " + str(index) + ": " + str(notes))
				song += generate_note_segment(notes, args['instrument'], slice_time)
		else:
			skip = False

	filename = args['name'] if not args['name'] == None else datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.wav")

	channel_type = args['channel_type'].lower()

	if channel_type == 'mono':
		logger.info("Exporting as mono.")
		song.set_channels(1)
		song.export("output/" + filename, format="wav")
	elif channel_type == 'stereo':
		logger.info("Exporting as stereo.")
		song.set_channels(2)
		song.export("output/" + filename, format="wav")
	else:
		logger.error("Invalid channel type provided, aborting.")