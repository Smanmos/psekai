# coding=utf-8
import sys
import re
import math
import csv
from fractions import Fraction


class MapElement:
    def __init__(self, type, bar, beat, ctrl = False):
        self.bar = bar
        self.beat = beat
        self.type = type
        self.ctrl = ctrl

    def time(self):
        return self.bar + self.beat

    def __lt__(self, other):
        if self.bar != other.bar:
            return self.bar < other.bar
        elif self.beat != other.beat:
            return self.beat < other.beat
        elif self.ctrl ^ other.ctrl:
            return self.ctrl
        elif self.ctrl and other.ctrl:
            return True
        elif self.left != other.left:
            return self.left < other.left
        elif self.right != other.right:
            return self.right < other.right
        else:
            return False



class Control(MapElement):
    def __init__(self, type, bar, beat):
        super().__init__(type, bar, beat, ctrl = True)

class Skill(Control):
    def __init__(self, bar, beat):
        super().__init__('skill', bar, beat)

    def __repr__(self):
        return f'Skill({self.bar}, {self.beat})'

class Fever(Control):
    def __init__(self, bar, beat):
        super().__init__('fever', bar, beat)

    def __repr__(self):
        return f'Fever({self.bar}, {self.beat})'

class BpmMarker(Control):
    def __init__(self, bar, beat, bpm):
        super().__init__('bpm', bar, beat)
        self.bpm = bpm

    def __repr__(self):
        return f'BpmMarker({self.bar}, {self.beat}, {self.bpm})'

class Note(MapElement):
    def __init__(self, type, bar, beat, left, right, flick = False, crit = False):
        super().__init__(type, bar, beat)
        self.crit = crit
        self.flick = flick
        self.left = left
        self.right = right

    def weight(self):
        if self.type == 'longmid':
            return Fraction(2,10) if self.crit else Fraction(1,10)
        elif self.flick:
            return 3 if self.crit else 1
        else:
            return 2 if self.crit else 1

    def __repr__(self):
        noterepr = f'Note({self.type}, {self.bar}, {self.beat}, {self.left}, {self.right}'
        if self.flick:
            noterepr = noterepr + ', flick = True'
        if self.crit:
            noterepr = noterepr + ', crit = True'
        noterepr += ')'
        return noterepr


class Tap(Note):
    def __init__(self, bar, beat, left, right, flick = False, crit = False):
        super().__init__('tap', bar, beat, left, right, flick, crit)

class Long(Note):
    def __init__(self, type, bar, beat, left, right, longid, flick = False, crit = False):
        super().__init__(type, bar, beat, left, right, flick, crit)
        self.longid = longid

    def __repr__(self):
        noterepr = f'Long({self.type}, {self.bar}, {self.beat}, {self.left}, {self.right}, {self.longid}'
        if self.flick:
            noterepr = noterepr + ', flick = True'
        if self.crit:
            noterepr = noterepr + ', crit = True'
        noterepr += ')'
        return noterepr

class LongStart(Long):
    def __init__(self, bar, beat, left, right, longid, flick = False, crit = False):
        super().__init__('longstart', bar, beat, left, right, longid, flick, crit)

class LongMid(Long):
    def __init__(self, bar, beat, left, right, longid, flick = False, crit = False):
        super().__init__('longmid', bar, beat, left, right, longid, flick, crit)

class LongEnd(Long):
    def __init__(self, bar, beat, left, right, longid, flick = False, crit = False):
        super().__init__('longend', bar, beat, left, right, longid, flick, crit)


class RawNote:
    def __init__(self, bar, beat, lane, width, type, prop, longid = None):
        self.bar = bar
        self.beat = beat
        self.lane = lane
        self.width = width
        self.type = type
        self.prop = prop
        self.longid = longid


    def __repr__(self):
        if self.type == 3:
            return f'RawNote({self.bar}, {self.beat}, {self.lane}, {self.width}, {self.type}, {self.prop}, {self.longid})'
        else:
            return f'RawNote({self.bar}, {self.beat}, {self.lane}, {self.width}, {self.type}, {self.prop})'
        #return "Note(" + str(self.bar) + ", " + str(self.beat) + ", " + str(self.lane) + ", " + str(self.width) + ", " + str(self.type) + ")"

    def __str__(self):
        if self.type == 3:
            return f'<note: time {self.bar}+{self.beat}, pos [{self.lane}, {self.lane + self.width - 1}], type {self.type}, prop {self.prop}, longid {self.longid}>'
        else:
            return f'<note: time {self.bar}+{self.beat}, pos [{self.lane}, {self.lane + self.width - 1}], type {self.type}, prop {self.prop}>'

# This part of this code is copied and adapted from:
# https://github.com/yp05327/PSKScoreMaker/blob/master/main.py
#####  define  #####
music_info_key_word = {
    'bpm': '#BPM(\d\d): (\d*)',
}
#####  read file  ######
def read_file(file_name):
    file_object = open('musicscore/' + file_name,'r')

    music_info = {}
    music_score = []

    read_step = 1
    try:
        for line in file_object:
            # get music info
            for key_word in music_info_key_word:
                info = re.match(music_info_key_word[key_word], line)
                if info:
                    #print(info.group(1), info.group(2))
                    music_info[int(info.group(1))] = int(info.group(2))


            info = re.match('#(\d\d\d)(\d)([0-9a-f]): ?(\w*)', line)

            if info:
                music_score.append({
                    'unitid': info.group(1),
                    'type': info.group(2),
                    'row': info.group(3),
                    'list': info.group(4),
                })
                continue

            info = re.match('#(\d\d\d)(\d)([0-9a-f])(\d):(\w*)', line)
            if info:
                music_score.append({
                    'unitid': info.group(1),
                    'type': info.group(2),
                    'row': info.group(3),
                    'longid': info.group(4),
                    'list': info.group(5),
                })
                continue

    finally:
        for key_word in music_info_key_word:
            if key_word not in music_info:
                music_info[key_word] = 'No info'

        file_object.close()

    music_score.sort(key=lambda x: x['unitid'])

    return music_info, music_score

# Count number of multiples of 1/8 between both ends, both exclusive
def num_eighths_between(start, end):
    if start == end:
        return 0
    else:
        return math.ceil(end * 8) - math.floor(start * 8) - 1

def eighths_between(start, end):
    step = math.floor(start * 8 + 1) * Fraction(1, 8)
    #print(type(step))
    #print(type(end))
    while True:
        if step >= end:
            break
        bar = math.floor(step)
        beat = step - bar
        yield bar, beat
        step = step + Fraction(1, 8)

def count_notes(notes):
    count = 0
    longstarts = [None] * 2
    prev = None
    for note in notes:
        if note.ctrl:
            continue
        for i in range(2):
            if longstarts[i] is not None:
                mids = num_eighths_between(prev.bar + prev.beat, note.bar + note.beat)
                if 8 % prev.beat.denominator == 0 and prev.bar + prev.beat != longstarts[i] and prev.bar + prev.beat != note.bar + note.beat:
                    mids += 1
                #print(mids, 'midpoints counted between', note, 'and', prev, 'for longid', i)
                count += mids
        count += 1
        #print('Counted:', note)
        if note.type == 'longstart':
            longstarts[note.longid] = note.bar + note.beat
        elif note.type == 'longend':
            longstarts[note.longid] = None
        prev = note
    return count

def get_total_weight(notes):
    weight = 0
    longstarts = [None] * 2
    prev = None
    for note in notes:
        if note.ctrl:
            continue
        for i in range(2):
            if longstarts[i] is not None:
                mids = num_eighths_between(prev.bar + prev.beat, note.bar + note.beat)
                if 8 % prev.beat.denominator == 0 and prev.bar + prev.beat != longstarts[i] and prev.bar + prev.beat != note.bar + note.beat:
                    mids += 1
                #print(mids, 'midpoints counted between', note, 'and', prev, 'for longid', i)
                weight += Fraction(1, 10) * mids
        weight += note.weight()
        #print('Counted:', note)
        if note.type == 'longstart':
            longstarts[note.longid] = note.bar + note.beat
        elif note.type == 'longend':
            longstarts[note.longid] = None
        prev = note
    return weight

def process_notes(music_info, music_score):
    raw_notes = []
    for obj in music_score:
        den = len(obj['list']) // 2
        for i in range(den):
            if int(obj['list'][i*2]) != 0 or int(obj['list'][i*2+1]) != 0:
                note = RawNote(int(obj['unitid']), Fraction(i, den), int(obj['row'], 16), int(obj['list'][2*i+1], 16), int(obj['type']), int(obj['list'][2*i]))
                #print(note)
                if note.type != 5 or note.prop in (1, 3, 4):
                    if note.type == 3:
                        note.longid = int(obj['longid'])
                    raw_notes.append(note)
    raw_notes = sorted(raw_notes, key = lambda d : (d.bar, d.beat, d.lane, d.type))
    for note in raw_notes:
        #if note.type == 0:
        #    print(note)
        pass

    notes = []
    longcrits = [None] * 2
    for note in raw_notes:
        if len(notes) > 0 and note.type != 0 and not notes[-1].ctrl and notes[-1].time() == note.bar + note.beat and notes[-1].left == note.lane:
            if note.type == 5:
                notes[-1].flick = True
            elif note.type == 3:
                if note.prop == 1:
                    notes[-1] = LongStart(note.bar, note.beat, note.lane, note.lane + note.width - 1, note.longid, crit = notes[-1].crit)
                    longcrits[notes[-1].longid] = notes[-1].crit
                elif note.prop == 2:
                    notes[-1] = LongEnd(note.bar, note.beat, note.lane, note.lane + note.width - 1, note.longid, crit = notes[-1].crit)
                    if longcrits[notes[-1].longid] is not None:
                        notes[-1].crit = notes[-1].crit or longcrits[notes[-1].longid]
                    longcrits[notes[-1].longid] = None
                elif note.prop == 3:
                    notes[-1] = LongMid(note.bar, note.beat, note.lane, note.lane + note.width - 1, note.longid, crit = notes[-1].crit)
                    if longcrits[notes[-1].longid] is not None:
                        notes[-1].crit = longcrits[notes[-1].longid]
                else:
                    notes.pop()

        else:
            if note.type == 1:
                if note.prop == 4:
                    notes.append(Skill(note.bar, note.beat))
                elif note.lane == 15:
                    if note.prop == 2:
                        notes.append(Fever(note.bar, note.beat))
                    else:
                        continue
                else:
                    notes.append(Tap(note.bar, note.beat, note.lane, note.lane + note.width - 1, crit = note.prop == 2))
            elif note.type == 5:
                notes.append(Note(note.bar, note.beat, note.lane, note.lane + note.width - 1, flick = True))
            elif note.type == 3:
                if note.prop == 1:
                    notes.append(LongStart(note.bar, note.beat, note.lane, note.lane + note.width - 1, note.longid))
                    longcrits[note.longid] = notes[-1].crit
                elif note.prop == 2:
                    notes.append(LongEnd(note.bar, note.beat, note.lane, note.lane + note.width - 1, note.longid))
                    if longcrits[notes[-1].longid] is not None:
                        notes[-1].crit = notes[-1].crit or longcrits[notes[-1].longid]
                    longcrits[note.longid] = None
                elif note.prop == 3:
                    notes.append(LongMid(note.bar, note.beat, note.lane, note.lane + note.width - 1, note.longid))
                    if longcrits[notes[-1].longid] is not None:
                        notes[-1].crit = longcrits[notes[-1].longid]
            elif note.type == 0:
                notes.append(BpmMarker(note.bar, note.beat, music_info[note.width]))
    notes = sorted(notes)
    return notes

def get_combo_multiplier(combo):
    if combo > 1000:
        return Fraction(11, 10)
    else:
        return 1 + Fraction(1, 100) * (combo // 100)

def beats_to_seconds(beats, bpm):
    return beats * Fraction(240) / bpm

SKILL_DURATION = 5
MIDPOINT_WEIGHT = Fraction(1, 10)
FEVER_MULTIPLIER = Fraction(3, 2)
DEBUG = False

def get_score_meta(notes, level, fever = False):
    note_count = count_notes(notes)
    level_multiplier = 1 + Fraction(level - 5, 200)
    total_weight = get_total_weight(notes)
    combo = 0
    base = 0
    skill_uptime = [0] * 6
    longstarts = [None] * 2
    skillNo = 0
    skill_time = 0
    skill_active = False
    fever_end = -1
    fever_notes = 0
    fever_score = 0
    prev = None
    bpm = None
    for note in notes:
        if prev is not None:
            if 8 % prev.beat.denominator == 0 and prev.time() != note.time():
                for i in range(0, 2):
                    if longstarts[i] is not None and prev.time() != longstarts[i]:
                        note_score = MIDPOINT_WEIGHT * get_combo_multiplier(combo)
                        if prev.time() <= fever_end:
                            fever_score += note_score
                            note_score *= FEVER_MULTIPLIER
                            fever_notes += 1
                            if fever_notes >= note_count // 10:
                                fever_end = prev.time()
                            if DEBUG:
                                print('Fever')
                        if skill_active:
                            skill_uptime[skillNo] += note_score
                            if DEBUG:
                                print('Skill', skillNo + 1)
                        if DEBUG:
                            print('Midpoint at', prev.bar, prev.beat, ', score =', float(note_score), ', combo = ', combo)
                        base += note_score
                        combo += 1
            for bar, beat in eighths_between(prev.time(), note.time()):
                for i in range(0, 2):
                    if longstarts[i] is not None:
                        note_score = MIDPOINT_WEIGHT * get_combo_multiplier(combo)
                        if bar + beat <= fever_end:
                            fever_score += note_score
                            note_score *= FEVER_MULTIPLIER
                            fever_notes += 1
                            if fever_notes >= note_count // 10:
                                fever_end = bar + beat
                            if DEBUG:
                                print('Fever')
                        if skill_active:
                            skill_time += (bar + beat - prev.time()) * Fraction(240) / bpm
                            if skill_time > SKILL_DURATION:
                                skill_active = False
                                skillNo += 1
                            else:
                                skill_uptime[skillNo] += note_score
                                if DEBUG:
                                    print('Skill', skillNo + 1)
                        if DEBUG:
                            print('Midpoint at', bar, beat, ', score =', float(note_score), ', combo =', combo)
                        base += note_score
                        combo += 1
                        prev = MapElement('dummy', bar, beat)
        if skill_active:
            skill_time += (note.time() - prev.time()) * Fraction(240) / bpm
            #print(skill_time)
            if skill_time > SKILL_DURATION:
                skill_active = False
                skillNo += 1
        if note.ctrl:
            #print(note)
            if note.type == 'fever':
                if fever:
                    fever_end = notes[-1].time()
            elif note.type == 'skill':
                skill_active = True
                skill_time = 0
            elif note.type == 'bpm':
                bpm = note.bpm
        else:
            note_score = note.weight() * get_combo_multiplier(combo)
            if note.time() <= fever_end:
                fever_score += note_score
                note_score *= FEVER_MULTIPLIER
                fever_notes += 1
                if fever_notes >= note_count // 10:
                    fever_end = note.time()
                if DEBUG:
                    print('Fever')
            if skill_active:
                skill_uptime[skillNo] += note_score
                if DEBUG:
                    print('Skill', skillNo + 1)
            if DEBUG:
                print(note, ', score =', float(note_score), ', combo = ', combo)
            base += note_score
            combo += 1
            if note.type == 'longstart':
                longstarts[note.longid] = note.time()
            elif note.type == 'longend':
                longstarts[note.longid] = None
        prev = note

    meta = {}
    meta['base'] = float(base * level_multiplier / total_weight)
    meta['fever'] = float(level_multiplier * fever_score / total_weight)
    skill_total = 0
    for i in range(6):
        meta[f'skill {i + 1}'] = float(level_multiplier * skill_uptime[i] / total_weight)
        skill_total += skill_uptime[i] / total_weight
    meta['skills'] = float(level_multiplier * skill_total)
    return meta

headers = ['name', 'diff', 'level', 'fever', 'base', 'skill 1', 'skill 2', 'skill 3', 'skill 4', 'skill 5', 'skill 6', 'skills']

def process_song(file_name, level, fever = False):
    info, score = read_file(file_name)
    notes = process_notes(info, score)
    meta = get_score_meta(notes, level, fever)
    return meta

def write_meta(file_name, level, fever = False):
    print(file_name, level, fever)
    meta = process_song(file_name, level, fever)
    name, diff = file_name.split('/')
    meta['name'] = name
    meta['diff'] = diff
    meta['level'] = level
    with open('data.csv', 'a', newline = '', encoding = 'utf-8') as f:
        w = csv.DictWriter(f, fieldnames = headers)
        w.writerow(meta)

def write_difficulties(song_name, levels, fever = False):
    diffs = ('easy', 'normal', 'hard', 'expert', 'master')
    for diff in diffs:
        if diff in levels.keys():
            print(levels[diff])
            write_meta(song_name + '/' + diff, levels[diff], fever)

def run(file_name):
    music_info, music_score = read_file(file_name)
    notes = process_notes(music_score)
    for note in notes:
        print(note)
        pass

def main(argv):
    run(argv[0])

if __name__ == "__main__":
    main(sys.argv[1:])
