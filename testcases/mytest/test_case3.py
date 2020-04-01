# -*- coding: utf-8 -*-

__author__ = 'chenlei'

import pytest



class TestMytest3:


    # 第一种参数化实现
    @pytest.mark.parametrize('input, output', [('30 + 40', 50), ('40 + 40', 80)])
    def test_third(self, input, output):
        '''
        使用parametrize实现参数化
        '''
        assert eval(input) == output


    # 第二种参数化实现
    @pytest.fixture(params=[1, 2, 3])
    def return_param(self, request):
        return request.param

    def test_fourth(self, return_param):
        '''
        使用fixture实现参数化
        '''
        assert return_param == 4







if __name__ == '__main__':
    pytest.main()