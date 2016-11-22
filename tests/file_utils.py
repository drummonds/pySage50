import os
from shutil import move


def remove_old_sage_import_files(filename, filename_end):
    rootDir = '.'
    for dirName, subdirList, fileList in os.walk(rootDir):
        if dirName[:6].lower() != r".\.git":
            print('Found directory: %s' % dirName)
            for fname in fileList:
                if fname[:len(filename_end)].lower() == filename_end:
                    os.remove(fname)
                    print('\t%s' % fname)
    saved_copy = filename + '.last'
    if os.path.isfile(saved_copy):  # Get rid of all old save copy
        os.remove(saved_copy)
    if os.path.isfile(filename):  # Copy the old file so that can inspect after test are run
        move(filename, saved_copy)

