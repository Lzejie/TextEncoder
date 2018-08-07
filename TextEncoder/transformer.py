# -*- coding: utf-8 -*-
# @Time    : 18/8/1 下午6:20
# @Author  : Edward
# @Site    :
# @File    : transformer.py
# @Software: PyCharm Community Edition

import re
import json
import pickle
from collections import defaultdict

import jieba


class Transformer(object):
    """
    将文本转化为索引序号，默认采用jiaba.cut作为分词方式，如果想采用字的方式，则使用list或自定义分词方式

    >>> t = Transformer(cutter=list, use_placeholder=True, max_length=10)
    >>> ss = ['abcde', 'cdefgg', 'scdea']
    >>> t.feed(ss)
    >>> isinstance(t.text_to_index('aacds'), list) and len(t.text_to_index('aacds')) > 0
    True
    >>> isinstance(t('aacds', fill=False), list) and len(t('aacds', fill=True)) > 0
    True
    >>> indexs = t('as12356df')
    >>> t.index_to_token(indexs)
    ['a', 's', '@', '@', '@', '@', '@', 'd', 'f']

    >>> t = Transformer(cutter=list, use_placeholder=False, max_length=10)
    >>> ss = ['abcde', 'cdefgg', 'scdea']
    >>> t.feed(ss)
    >>> isinstance(t.text_to_index('aacds'), list) and len(t.text_to_index('aacds')) > 0
    True
    >>> isinstance(t('aacds'), list) and len(t('aacds')) > 0
    True
    >>> isinstance(t('', fill=False), list) and len(t('', fill=False)) == 0
    True
    """

    cutter_dict = {
        'list': list,
        'jieba': jieba.cut
    }

    def __init__(
            self,
            cutter='jieba',
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

    def __call__(self, text, fill=True):
        return self.text_to_index(text, fill=fill)

    def __getitem__(self, index):
        return self.index_token.get(index, self.UNK)

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
        leave_tokens = set([self.STR, self.END, self.UNK] + leave_tokens)
        self.token_index = dict(zip(leave_tokens, range(len(leave_tokens))))
        self.index_token = dict(zip(range(len(leave_tokens)), leave_tokens))

    def transform_2_words(self, text, fill=True):
        '''
        文本预处理入口
        :param text: 待处理文本
        :return: str
        '''
        new_line = self.STR + self.pretreat(text) + self.END
        tokens = Transformer.cutter_dict[self.cutter](new_line)
        if fill:
            return tokens[:self.max_length] + [self.UNK] * max((self.max_length - len(tokens)), 0)
        else:
            return tokens[:self.max_length]

    def text_to_index(self, text, fill=True):
        '''
        文本转化为索引
        :param text: 待转化文本
        :return: [int, int, ... , int]
        '''
        return self.token_to_index(self.transform_2_words(text, fill=fill))

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

    def save(self, path):
        save_data = {
            'cutter': self.cutter,
            'max_length': self.max_length,
            'token_frequence': self.token_frequence,
            'stop_words': tuple(self.stop_words),
            'STR': self.STR,
            'END': self.END,
            'UNK': self.UNK,
            'token_index': self.token_index,
            'index_token': self.index_token,
            'tokens': tuple(self.tokens),
        }

        with open(path, 'w') as f:
            json.dump(save_data, f)
        # with open(path, 'w') as f:
        #     pickle.dump(self, f)


    @staticmethod
    def restore(path):
        with open(path) as f:
            data = json.load(f)
        transformer = Transformer(
            cutter=data['cutter'],
            stop_words=set(data['stop_words']),
            max_length=data['max_length'],
            STR=data['STR'],
            END=data['END'],
            UNK=data['UNK'],
            token_frequence=data['token_frequence'],
        )

        transformer.token_index = {
            k: int(v)
            for k, v in data['token_index'].items()
        }
        transformer.index_token = {
            int(k): v
            for k,v in data['index_token'].items()
        }
        transformer.tokens = set(data['tokens'])

        return transformer
        # with open(path) as f:
        #     return pickle.load(f)

if __name__ == '__main__':
    # import doctest
    # doctest.testmod()

    t = Transformer(cutter='list', use_placeholder=True)
    ss = ['abcde', 'cdefgg', 'scdea']
    t.feed(ss)
    indexs = t('aacds1')
    print(indexs)
    print(t.index_to_token(indexs))

    t.save('../tmp')
    t = Transformer.restore('../tmp')

    indexs = t('aacds1')
    print(indexs)
    print(t.index_to_token(indexs))
