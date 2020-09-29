import sys
import time
import os

class Formatter():
    def __init__(self,fileName,_version_,creator,contributors = ["N","o","n","e"]):
        self.columns = 120
        self.rows = 10
        self.fileName = fileName
        self._version_ = _version_
        self.creator = creator
        self.contributors = ", ".join(contrib for contrib in contributors)

    def header(self):
        try:
            os.system("cls")
        except:
            os.system("clear")
        print("-"*self.columns)
        print("\n"+"{:^120}".format(("welcome to "+self.fileName).upper()))
        print("{:^120}".format("Version "+self._version_))
        print("{:^120}".format("Created by "+self.creator))
        if self.contributors != "N, o, n, e" and self.contributors != "":
            print("{:^120}".format("with help from "+self.contributors))
        print("\n"+"-"*self.columns)

if __name__ == "__main__":
    test = formatter("Test","1.0.0","dmcanady")
    test.header()
