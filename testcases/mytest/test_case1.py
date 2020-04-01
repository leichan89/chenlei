# -*- coding: utf-8 -*-

__author__ = 'chenlei'

import pytest



class TestMytest1:

    def setup(self):
        print('\n' + '我是setup')


    def get_data(self):
        return 5

    def test_first(self):
        '''
        我是第一个用例
        '''
        print('\n' + '我是case1')
        assert 'a' == 'a', '失败'

    def test_second(self):
        '''
        我是第二个用例
        '''
        print('\n' + '我是case2')
        assert self.get_data() == 6

    def teardown(self):
        print('\n' + '我是teardown')






if __name__ == '__main__':
    pytest.main()