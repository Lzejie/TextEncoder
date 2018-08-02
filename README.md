# TextEncoder
文本预处理，简化机器学习训练前的数据清洗工作

## Quick Start
安装
```shell
sudo pip install TextEncoder
```

使用
```python
>>> t = Transformer(cutter=list, use_placeholder=True)
>>> ss = ['abcde', 'cdefgg', 'scdea']
>>> t.feed(ss)

>>> t.text_to_index('aacds')
[0, 5, 5, 3, 4, 6, 1]
>>> t('aacds')
[0, 5, 5, 3, 4, 6, 1]

>>> indexs = t('as12356df')
>>> indexs
[3, 8, 12, 2, 2, 2, 2, 2, 7, 10, 5]

>>> t.index_to_token(indexs)
['a', 's', '@', '@', '@', '@', '@', 'd', 'f']

>>> t = Transformer(cutter=list, use_placeholder=False)
>>> ss = ['abcde', 'cdefgg', 'scdea']
>>> t.feed(ss)

>>> indexs = t.text_to_index('aacds')
>>> indexs
[6, 6, 5, 3, 10]
>>> t.index_to_token(indexs)
['a', 'a', 'c', 'd', 's']
```
