# -*- coding: utf-8 -*-

__author__ = 'chenlei'

import pytest



class TestMytest2:

    @pytest.fixture()
    def myfixture1(self):
        print('\n' + '每个case都执行myfixture1')

    @pytest.fixture()
    def myfixture2(self):
        print('\n' + '每个case都执行myfixture2')
        yield
        print('我是myfixture2的teardown')

    @pytest.fixture(autouse=True)
    def myfixture3(self):
        print('\n' + '每个case都执行myfixture3')
        yield
        print('我是myfixture3的teardown')


    # 调用fixture的第一种方式
    def test_first(self, myfixture1, myfixture2):
        '''
        我是第一个用例
        '''
        print('\n' + '我是case1')
        assert 4 == 5

    # 调用fixture的第二种方式
    @pytest.mark.usefixtures('myfixture1', 'myfixture2')
    def test_second(self):
        '''
        我是第二个用例
        '''
        print('\n' + '我是case2')
        assert 4 == 5







if __name__ == '__main__':
    pytest.main()