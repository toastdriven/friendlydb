# Green the world, baby.
from gevent import monkey
monkey.patch_all()

from friendlydb import __version__
from friendlydb.db import FriendlyDB


if __name__ == '__main__':
    from optparse import OptionParser
    import sys

    parser = OptionParser()
    parser.add_option("-d", "--data", dest="data_directory", help="The directory to store the data in.")
    parser.add_option("-w", "--width", dest="hash_width", type="int", default=None, help="Defines the width of the hashes.")
    (options, args) = parser.parse_args()

    if not options.data_directory:
        print("The -d flag is required!")
        sys.exit()

    fdb = FriendlyDB(options.data_directory, options.hash_width)
    # FIXME: Get the web server interface going.
    # fdb.run()
