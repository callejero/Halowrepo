#===============================================================================
# LICENSE Retrospect-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================

import cPickle as pickle
import base64

from logger import Logger


class Pickler:
    # store some vars for speed optimization
    __PickleContainer = dict()        # : storage for pickled items to prevent duplicate pickling
    __Base64Chars = {"\n": "-",
                     "=": "%3d",
                     "/": "%2f",
                     "+": "%2b"}

    def __init__(self):
        pass

    @staticmethod
    def DePickleMediaItem(hexString):
        """De-serializes a serialized mediaitem

        Arguments:
        hexString : string - Base64 encoded string that should be decoded.

        Returns:
        The object that was Pickled and Base64 encoded.

        """

        hexString = hexString.rstrip(' ')
        hexString = reduce(lambda x, y: x.replace(Pickler.__Base64Chars[y], y), Pickler.__Base64Chars, hexString)

        Logger.Trace("DePickle: HexString: %s (might be truncated)", hexString[0:256])

        # Logger.Trace("DePickle: HexString: %s", hexString)
        pickleString = base64.b64decode(hexString)
        # Logger.Trace("DePickle: PickleString: %s", pickleString)
        pickleItem = pickle.loads(pickleString)
        return pickleItem

    @staticmethod
    def PickleMediaItem(item):
        """Serialises a mediaitem

        Arguments:
        item : MediaItem - the item that should be serialized

        Returns:
        A pickled and base64 encoded serialization of the <item>.

        """

        if item.guid in Pickler.__PickleContainer:
            Logger.Trace("Pickle Container cache hit")
            return Pickler.__PickleContainer[item.guid]

        pickleString = pickle.dumps(item)
        # Logger.Trace("Pickle: PickleString: %s", pickleString)
        hexString = base64.b64encode(pickleString)

        # if not unquoted, we must replace the \n's for the URL
        hexString = reduce(lambda x, y: x.replace(y, Pickler.__Base64Chars[y]), Pickler.__Base64Chars, hexString)

        # Logger.Trace("Pickle: HexString: %s", hexString)

        Pickler.__PickleContainer[item.guid] = hexString
        return hexString

    @staticmethod
    def Validate(test, raiseOnMissing=False, logger=None):
        """ Validates if in instance has all properties after depickling. The __class__ of the 'test' should
         implement a self.__dir__(self) that returns the required attributes.

        @param test:            Item to test
        @param raiseOnMissing:  If True an error will be raised on failure
        @param logger           Pass a loger in

        @return None if no error, or an error message if an error occurred.
        """

        for attribute in dir(test):
            if logger is not None:
                logger.Trace("Testing: %s", attribute)

            # manage private attributes
            if attribute.startswith("__"):
                attribute = "_%s%s" % (test.__class__.__name__, attribute)

            if not hasattr(test, attribute):
                error = "Attribute Missing: %s" % attribute

                if logger is not None:
                    logger.Warning(error)
                if raiseOnMissing:
                    raise Exception(error)
                return error

        # We are good
        return None
