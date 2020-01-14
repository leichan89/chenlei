#coding=utf-8

class ResponseError(Exception):

    def __init__(self, errmsg):
        Exception.__init__(self, errmsg)

class CodeError(Exception):

    def __init__(self, errmsg):
        Exception.__init__(self, errmsg)

class ParamsError(Exception):

    def __init__(self, errmsg):
        Exception.__init__(self, errmsg)

class IndexOutOfBoundsError(Exception):

    def __init__(self, errmsg):
        Exception.__init__(self, errmsg)


class ObjectInitError(Exception):

    def __init__(self, errmsg):
        Exception.__init__(self, errmsg)


class ExcelParamIsEmptyError(Exception):

    def __init__(self, errmsg):
        Exception.__init__(self, errmsg)