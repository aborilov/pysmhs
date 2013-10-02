import unittest
from pysmhs import datehandler


class TestDatehandler(unittest.TestCase):

    def setUp(self):
        configfile = "test/dateconfig.txt"
        self.d = datehandler.datehandler(params={'configfile': configfile})
        self.d.start()

    def testDate(self):
        print("")
        print(self.d.tags)
        # print(self.d.gettag('date'))
        # self.d.checktags()


if __name__ == '__main__':
    unittest.main()
