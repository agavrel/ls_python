import os
import sys
import stat # file permission
import datetime # to convert epoch time to date
from pwd import getpwuid # to translate uid into its string value
from grp import getgrgid # to translate gid into its string value
import functools # to mimic ls behavior for sorting files

####### ls-like main function
def my_ls(argv):
    inputs = []
    flags = "" # no flags by default
    for i in range(0, len(argv)): # handle multi arguments
        s = argv[i]
        if len(s) > 0:
            if s.startswith("-"):
                flags += s[1:]
            else:
                inputs.append(s)
    flags = "".join(set(flags)) # remove duplicate letters (flags)
    if not inputs:
        inputs.append('.')  # current directory by default

    ####### main program
    output = []
    folders = []
    files = []
    for input in inputs:
        if not os.path.exists(input):
            output.append(f"ls: cannot access '{input}': No such file or directory")
        elif os.path.isfile(input): # search file in relative path
            files.append(input)
        elif os.path.isdir(input):
            folders.append(input)

    files = sorted(files, key=functools.cmp_to_key(my_cmp))
    if files:
        output.append(list_files(input, files, flags))

    for folder in folders:
        res = ""
        if len(folders) > 1: # ls will add folder name if some files have been printed before
            res = f"{folder}:"
        listing = os.listdir(folder)
        filenames = sorted(listing, key=functools.cmp_to_key(my_cmp))
        if filenames and res != "":
            res += '\n'
        res += list_files(folder, filenames, flags)
        if res:
            output.append(res)

    if output:
        res = "\n\n".join(output)
        print(res)
        return res # return output to allow unittests
    return ""



####### list files function
def list_files(directory, filenames, flags):
    files = []
    res = ""
    if 'l' in flags:
        total_size = int(0)
        files_info = []
        nlink_padding, gid_padding, uid_padding, size_padding = 0, 0, 0, 0
        for filename in filenames:
            file_path = os.path.join(directory, filename)
            if not os.path.exists(file_path):
                files.append(f"ls: cannot access '{file_path}': No such file or directory")
                continue
            if filename.startswith("."): # hidden file, requires flag 'a'
                continue
            file_stat = os.stat(os.path.abspath(file_path))
            nlink = file_stat.st_nlink
            gid = getgrgid(file_stat.st_gid).gr_name
            uid = getpwuid(file_stat.st_uid).pw_name
            size = file_stat.st_size
            total_size += file_stat.st_blocks
            file_info = FileInfo(file_stat.st_mode, str(nlink), gid, uid, file_stat.st_mtime, str(size), filename)
            nlink_padding = max(len(str(nlink)), nlink_padding)
            uid_padding = max(len(uid), uid_padding) # for padding purpose...
            gid_padding = max(len(gid), gid_padding)
            size_padding = max(len(str(size)), size_padding)
            if os.path.isdir(file_path):   # asked to return only files and not directories
                continue
            files_info.append(file_info)
        if len(files_info)> 1:
            total_size = int(total_size / 2)
            res += "total {}\n".format(total_size)
        for file_info in files_info:
            files.append(file_info.to_string((nlink_padding, uid_padding, gid_padding, size_padding)))

    else:
        for filename in filenames:
            if filename.startswith("."): # hidden file, requires flag 'a'
                continue
            file_path = os.path.join(directory, filename)
            if os.path.isdir(file_path):   # asked to return only files and not directories
                continue
            files.append(filename)
    return res + "\n".join(files)



####### handle of os.stat(file)
class FileInfo:
    def __init__(self, filemode, nlink, gid, uid, timestamp, size, name):
        self.filemode = filemode
        self.nlink = nlink
        self.gid = gid
        self.uid = uid
        self.timestamp = timestamp
        self.size = size
        self.name = name

    def to_string(self, pad):
        # NB: Might depend on local for day (%d) and month (%b) order:
        date = datetime.datetime.fromtimestamp(self.timestamp)
        if date.year < datetime.date.today().year: # ls display the year instead of the time when it was the precedent one
            date = f"{date.strftime('%b')} {str(date.day).rjust(2)} {str(date.year).rjust(5)}"
        else:
            date = f"{date.strftime('%b')} {str(date.day).rjust(2)} {str(date.hour).rjust(2, '0')}:{str(date.minute).rjust(2, '0')}"
        permission = stat.filemode(self.filemode)
        return f"{permission} {self.nlink.rjust(pad[0])} {self.uid.rjust(pad[1])} {self.gid.rjust(pad[2])} {self.size.rjust(pad[3])} {date} {self.name}"



####### custom function cmp that mimics the way ls display results
def my_cmp(a, b):
    a = a.lower().replace(".", "").replace('_', '') # ls ignores the dots and dashes when it sorts filenames
    b = b.lower().replace(".", "").replace('_', '')
    if len(b) < len(a):
        return -my_cmp(b, a)  # make sure 'a' is the shortest string to avoid buffer overflow
    for i in range(len(a)):
        if a[i] != b[i]:
            return ord(a[i]) - ord(b[i]) # returns difference in char values
    return -1 # ls returns the longest first if 'a' is a substring of 'b'


def main():
    my_ls(sys.argv[1:])

if __name__ == "__main__":
    main()