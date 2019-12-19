import CTypeGen
import CMock
import ctypes
import sys

'''
This test ensures that calling "realfunc" from the mock works.
We call "callme" from our test library, and it should call "mockme" with the
same args passed to callme, and return the result.
The "real" mockme returns the first arg passed to it.

'''

libname = sys.argv[1] if len( sys.argv ) > 2 else "./libChainTest.so"
module, res = CTypeGen.generate( libname, "chaintest.py",
                                 [], [ "mockme", "callme" ]  )

lib = ctypes.CDLL( libname )
module.decorateFunctions(lib)

@CMock.Mock(lib.mockme, lib)
def mocked(one, two, three):
    print("I mock you: %d %d %d" % (one, two, three))
    rc = mocked.realfunc(three, two, one)
    assert rc == three
    return two

rc = lib.callme(1, 2, 3)
assert rc == 2

