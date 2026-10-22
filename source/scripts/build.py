# -*- coding: utf-8 -*-
"""把 plan.json 注入 template.html，产出单文件周末指南页面。

用法：
    python build.py --data plan.json --out weekend.html
    python build.py --data plan.json --out weekend.html --template ../assets/template.html

不传 --template 时，默认使用脚本同级 ../assets/template.html。
"""
from __future__ import print_function

import argparse
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TPL = os.path.join(HERE, '..', 'assets', 'template.html')

REQUIRED_CITY = ['name', 'sub', 'stores', 'insights', 'route']
REQUIRED_STORE = ['n', 'a', 'tags', 'd', 'c', 'end']


def die(msg):
    sys.stderr.write('BUILD FAILED: %s\n' % msg)
    sys.exit(2)


def need(obj, keys, where):
    missing = [k for k in keys if k not in obj or obj[k] in (None, '', [], {})]
    if missing:
        die('%s 缺少字段: %s' % (where, ', '.join(missing)))


def validate(d):
    need(d, ['docTitle', 'sigLeft', 'sigRight', 'hero', 'order', 'cities', 'cityIntro', 'cmpHead', 'generatedAt',
             'burger', 'combo', 'coupons', 'pricing', 'activity', 'plans', 'source'], 'plan')
    need(d['hero'], ['kicker', 'title', 'lede', 'stats'], 'hero')
    need(d['burger'], ['price', 'craftCost', 'storeLabel'], 'burger')
    need(d['combo'], ['price', 'total'], 'combo')
    need(d['pricing'], ['couponBurger', 'chicken2', 'set3',
                        'soloBurger', 'soloChicken', 'soloFries'], 'pricing')
    need(d['activity'], ['sub', 'items'], 'activity')
    need(d['source'], ['body', 'codes'], 'source')

    if not isinstance(d['order'], list) or not d['order']:
        die('order 必须是非空数组')
    for k in d['order']:
        if k not in d['cities']:
            die('order 里的 %r 在 cities 中不存在' % k)

    for k in d['order']:
        c = d['cities'][k]
        need(c, REQUIRED_CITY, 'cities.%s' % k)
        need(c['route'], ['t', 'steps'], 'cities.%s.route' % k)
        if not c['stores']:
            die('cities.%s.stores 为空' % k)
        for i, st in enumerate(c['stores']):
            need(st, REQUIRED_STORE, 'cities.%s.stores[%d]' % (k, i))
            if not isinstance(st['tags'], list) or not st['tags']:
                die('cities.%s.stores[%d].tags 必须是非空数组' % (k, i))
            for j, tg in enumerate(st['tags']):
                if not isinstance(tg, list) or len(tg) < 1:
                    die('cities.%s.stores[%d].tags[%d] 必须是 [文案, 样式] 数组' % (k, i, j))
        if not c['insights']:
            die('cities.%s.insights 为空' % k)

    if not d['coupons']:
        die('coupons 不能为空（券池计算依赖前 3 张券）')
    if len(d['coupons']) < 3:
        die('coupons 至少需要 3 张：堡券 / 炸鸡券 / 免费小食券')
    for i, cp in enumerate(d['coupons']):
        need(cp, ['amt', 'name', 'note', 'short'], 'coupons[%d]' % i)

    if not d['plans']:
        die('plans 不能为空')
    for i, p in enumerate(d['plans']):
        need(p, ['name', 'tag', 'combo', 'kcal', 'price'], 'plans[%d]' % i)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--template', default=DEFAULT_TPL)
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()

    if not os.path.exists(a.data):
        die('找不到数据文件 %s' % a.data)
    if not os.path.exists(a.template):
        die('找不到模板 %s' % a.template)

    try:
        data = json.load(io.open(a.data, encoding='utf-8'))
    except ValueError as e:
        die('plan.json 不是合法 JSON：%s' % e)

    validate(data)

    tpl = io.open(a.template, encoding='utf-8').read()
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    # 避免数据里的 </script> 提前截断内联脚本
    payload = payload.replace('</', '<\\/')

    marker = '<script>'
    if tpl.count(marker) != 1:
        die('模板里应恰好有 1 个 <script> 标签，实际 %d 个' % tpl.count(marker))
    i = tpl.index(marker) + len(marker)
    out = tpl[:i] + '\nwindow.__PLAN__ = ' + payload + ';\n' + tpl[i:]

    out_dir = os.path.dirname(os.path.abspath(a.out))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    io.open(a.out, 'w', encoding='utf-8', newline='\n').write(out)

    if not a.quiet:
        names = [data['cities'][k]['name'] for k in data['order']]
        total = sum(len(data['cities'][k]['stores']) for k in data['order'])
        print('OK  %s' % a.out)
        print('    %d 个片区 / %d 家门店 / %d 张券 / %d 个方案'
              % (len(data['order']), total, len(data['coupons']), len(data['plans'])))
        print('    %s' % ' · '.join(names))
        print('    %.0f KB' % (len(out.encode('utf-8')) / 1024.0))


if __name__ == '__main__':
    main()
