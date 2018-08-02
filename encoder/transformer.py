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
    '''
    将文本转化为索引序号，默认采用jiaba.cut作为分词方式，如果想采用字的方式，则使用list或自定义分词方式

    >>> t = Transformer(cutter=list, use_placeholder=False)
    >>> ss = ['abcde', 'cdefgg', 'scdea']
    >>> t.feed(ss)
    >>> isinstance(t.text_to_index('aacds'), list) and len(t.text_to_index('aacds')) > 0
    True
    >>> isinstance(t('aacds'), list) and len(t('aacds')) > 0
    True
    >>> t('')
    []
    >>> indexs = t('asdf')
    >>> t.index_to_text(indexs)
    'asdf'
    '''
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
        for line in texts:
            for token in set(self.transform_2_words(line)):
                self.tokens[token] += 1
        leave_tokens = [item[0]
            for item in sorted(
                filter(
                    lambda x: x[1] > self.token_frequence,
                    self.tokens.items()
                ), key=lambda x: -x[1]
            )
        ]
        self.token_index = dict(zip(leave_tokens, range(len(leave_tokens))))
        self.index_token = dict(zip(range(len(leave_tokens)), leave_tokens))

    def transform_2_words(self, line):
        new_line = self.STR + self.pretreat(line) + self.END
        tokens = self.cutter(new_line)
        return tokens[:self.max_length]

    def token_encode(self, tokens):
        assert isinstance(tokens, list), 'token必须为列表'
        return [self.token_index.get(token, self.UNK) for token in tokens]

    def text_to_index(self, text):
        return self.token_encode(self.transform_2_words(text))

    def index_to_text(self, indexs):
        return ''.join([
            self.index_token[index]
            for index in indexs
            if self.index_token[index] not in [self.STR, self.END, self.UNK]
        ])


if __name__ == '__main__':
    import doctest
    doctest.testmod()
