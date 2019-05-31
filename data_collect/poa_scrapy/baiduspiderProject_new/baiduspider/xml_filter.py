# -*- coding: utf-8 -*-
# 提取标签及子标签的纯文本
def xml_filter(content):
    con_filter = ""
    con_list = content.split('<')
    for con in con_list:
        con_filter = con_filter+"".join(con.split('>')[1:])
    return con_filter
