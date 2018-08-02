# -*- coding: utf-8 -*-
# @Time    : 18/8/1 下午6:20
# @Author  : Edward
# @Site    :
# @File    : transformer.py
# @Software: PyCharm Community Edition

import re
from collections import defaultdict

import jieba


class Transformer(object):
    """
    将文本转化为索引序号，默认采用jiaba.cut作为分词方式，如果想采用字的方式，则使用list或自定义分词方式

    >>> t = Transformer(cutter=list, use_placeholder=True)
    >>> ss = ['abcde', 'cdefgg', 'scdea']
    >>> t.feed(ss)
    >>> isinstance(t.text_to_index('aacds'), list) and len(t.text_to_index('aacds')) > 0
    True
    >>> isinstance(t('aacds'), list) and len(t('aacds')) > 0
    True
    >>> indexs = t('as12356df')
    >>> t.index_to_token(indexs)
    ['a', 's', '@', '@', '@', '@', '@', 'd', 'f']

    >>> t = Transformer(cutter=list, use_placeholder=False)
    >>> ss = ['abcde', 'cdefgg', 'scdea']
    >>> t.feed(ss)
    >>> isinstance(t.text_to_index('aacds'), list) and len(t.text_to_index('aacds')) > 0
    True
    >>> isinstance(t('aacds'), list) and len(t('aacds')) > 0
    True
    >>> isinstance(t(''), list) and len(t('')) == 0
    True
    """

    def __init__(
            self,
            cutter=jieba.cut,
            max_length=30,
            token_frequence=0,
            pretreat=lambda s: re.sub('[\t\n\r ]', '', s),
            stop_words=set(),
            STR='#',
            END='&',
            UNK='@',
            use_placeholder=True,
    ):
        '''
        初始化文本编码器转化器

        :param cutter: 分词器
        :param max_length: 文本最大长度
        :param token_frequence: 最小出现频次
        :param pretreat: 文本预处理函数
        :param stop_words: 停用词
        :param STR: 开始标识符
        :param END: 结尾标识符
        :param UNK: 未知标识符
        :param use_placeholder: 是否使用标识符True/False
        '''
        # 分词器
        self.cutter = cutter
        # 文本最大长度
        self.max_length = max_length

        self.token_frequence = token_frequence
        # 文本预处理函数
        self.pretreat = pretreat
        # 停用词
        self.stop_words = set(stop_words)
        if use_placeholder:
            # 文本开头
            self.STR = STR
            # 文本结尾
            self.END = END
            # 未知的词语
            self.UNK = UNK
        else:
            self.STR = ''
            self.END = ''
            self.UNK = ''
        # 词->index
        self.token_index = {}
        # index->词
        self.index_token = {}
        # token以及其出现的次数
        self.tokens = defaultdict(int)

    def __call__(self, text):
        return self.text_to_index(text)

    def feed(self, texts):
        '''
        传入语料

        :param texts: 语料列表
        '''
        for line in texts:
            for token in set(self.transform_2_words(line)):
                self.tokens[token] += 1
        leave_tokens = [
            item[0] for item in sorted(
                filter(
                    lambda x: x[1] > self.token_frequence,
                    self.tokens.items()
                ), key=lambda x: -x[1]
            )
        ]
        leave_tokens = [self.STR, self.END, self.UNK] + leave_tokens
        self.token_index = dict(zip(leave_tokens, range(len(leave_tokens))))
        self.index_token = dict(zip(range(len(leave_tokens)), leave_tokens))

    def transform_2_words(self, text):
        '''
        文本预处理入口
        :param text: 待处理文本
        :return: str
        '''
        new_line = self.STR + self.pretreat(text) + self.END
        tokens = self.cutter(new_line)
        return tokens[:self.max_length]

    def text_to_index(self, text):
        '''
        文本转化为索引
        :param text: 待转化文本
        :return: [int, int, ... , int]
        '''
        return self.token_to_index(self.transform_2_words(text))

    def token_to_index(self, tokens):
        '''
        token列表转化为索引
        :param tokens: 待转化token列表
        :return: [int, int, ... , int]
        '''
        filted_tokens = [token if token in self.tokens else self.UNK for token in tokens]
        return [self.token_index[token] for token in filted_tokens]

    def index_to_token(self, indexs):
        '''
        索引转化为token
        :param indexs: 索引列表
        :return: [str, str, ... , str]
        '''
        return [
            self.index_token.get(index, self.UNK)
            for index in indexs
            if self.index_token.get(index) not in [self.STR, self.END] and self.index_token.get(index)
        ]


if __name__ == '__main__':
    # import doctest
    # doctest.testmod()



    t = Transformer(cutter=list, use_placeholder=False)
    ss = ['abcde', 'cdefgg', 'scdea']
    t.feed(ss)
    indexs = t('aacds1')
    print(indexs)
    print(t.index_to_token(indexs))
