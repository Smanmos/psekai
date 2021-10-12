import sys
import score_analyzer

def run(args):
    if len(args) != 6:
        print('Usage: meta_writer.py <file name> <5 diff values>')
        return 
    else:
        file_name = args[0]
        diff_names = ('easy', 'normal', 'hard', 'expert', 'master')
        diffs = {diff_names[i]: int(args[i+1]) for i in range(5)}
        score_analyzer.write_difficulties(file_name, diffs, fever=False)
        score_analyzer.write_difficulties(file_name, diffs, fever=True)

if __name__ == '__main__':
    run(sys.argv[1:])
    