# -*- coding: utf-8 -*-
# @Time    : 18/7/27 下午5:01
# @Author  : Edward
# @Site    :
# @File    : setup.py
# @Software: PyCharm Community Edition

from setuptools import setup, find_packages

setup(
    name="TextEncoder",
    packages=find_packages(),
    version='0.1.6',
    description="text TextEncoder",
    author="L_zejie",
    author_email='lzj_xuexi@163.com',
    url="https://github.com/Lzejie/TextEncoder",
    license="MIT Licence",
    keywords=['text', 'encoder', 'nlp'],
    classifiers=[],
    install_requires=[
        'jieba'
    ]
)
