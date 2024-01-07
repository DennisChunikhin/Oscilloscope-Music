import warnings

# Convert midi note to frequency
def note_to_freq(note):
    return 440 * 2**((note-69)/12)

# Get tempo
def get_tempo(track):
    for msg in track:
        if msg.type=='set_tempo':
            return msg.tempo
    
    return None

# Get time signature
def get_time_sig(track):
    for msg in track:
        if msg.type=='time_signature':
            return (msg.numerator, msg.denominator)
    
    return (4,4) # Default time signature

# Get notes from midi track
def track_to_freqs(track, bpm, ticks_per_beat, ignore_rests=False):
    durations, freqs = [], []
    
    on = False
    for msg in track:
        # Make sure message is to play the note and issue a warning if a chord is played
        if msg.type == 'note_on' and msg.velocity != 0:
            if on:
                warnings.warn(f"Two or more notes are played at the same time on channel {msg.channel}. Only the sequentially first note will be played.")
            on = True
        else:
            if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                on = False
                durations.append(msg.time/ticks_per_beat/bpm*60)
            continue

        if msg.time != 0:
            time = msg.time/ticks_per_beat/bpm*60
            if not durations or not ignore_rests:
                freqs.append(0)
                durations.append(time)
            else:
                durations[-1] = durations[-1] + time

        freqs.append(note_to_freq(msg.note))
    
    return durations, freqs