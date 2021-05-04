from ls import my_ls
import unittest
import subprocess # to call real 'ls' function
import glob # to allow '*' tests

def original_ls(argv):
    my_command = f"ls -1 --file-type {' '.join(argv)} | grep -v '/' " # only list files
    original_function = subprocess.getoutput(my_command)
    return original_function

class TestStringMethods(unittest.TestCase):
    def test_ls(self):
        argv = [""]
        self.assertEqual(my_ls(argv), original_ls(argv))
    def test_non_existing_file(self):
        argv = ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa_does_not_exists.txt"]
        self.assertEqual(my_ls(argv), original_ls(argv))
    def test_existing_file(self):
        argv = ["ls.py"]
        self.assertEqual(my_ls(argv), original_ls(argv))
    def test_existing_file_start_with(self):
        argv = glob.glob("ls*")
        self.assertEqual(my_ls(argv), original_ls(argv))
    #def test_existing_folder_with_empty_files(self): # create folder first
    #    argv = ["test"]
    #    self.assertEqual(my_ls(argv), original_ls(argv))
    def test_ls_with_file_extension(self):
        argv = glob.glob("*.py")
        self.assertEqual(my_ls(argv), original_ls(argv))
    def test_ls_with_star(self):
        argv = glob.glob("*")
        self.assertEqual(my_ls(argv), original_ls(argv)) # we are currently only handling files so it will have the same behavior
    def test_with_l_flag(self):
        argv = ["-l"]
        self.assertEqual(my_ls(argv), original_ls(argv))
    def test_with_absolute_path(self):
        argv = ["/home"]
        self.assertEqual(my_ls(argv), original_ls(argv))

    # TODO: Implement unitests for chmod (cannot access file)
    # TODO: Implement symlink representation


if __name__ == '__main__':
    unittest.main()
