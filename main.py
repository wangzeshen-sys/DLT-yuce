# -*- coding: utf-8 -*-
#
#                                                                                          #
#            ##                                ##                                          ##        ###
#            ##                          ###   ###                                        ###        ##
#            ##                 ##        ##   ##          #####################          ########   #########
#            ##                  ##   ###############      #####################         #########  ##########
#            ##                  ###  ###############       #      ##          #        ###  ##    ###  #
#            ##                   #         ##                     ###                 ###    ##   ##   ##
#            ##                             ##                    ###                  ##     #    #    ##
#  ######################               ###########              ###     ##                ##
#  ######################      #####    ###########             ###      ####              ##   ############
#           ###                #####    ##       ##            ###        ####              ##  ############
#           ###                   ##    ###########         ###################             ##            ##
#           ####                 ##     ###########         ####################         ##               ##
#           ####                 ##     ##       ##          #####   ##      ###         ##   #########   ##
#           ## #                ###     ##       ##                  ##       #          ##   ##     ##   ##
#          ### ##               #####   ###########                  ##                  ##   ##     ##   ##
#          ##  ###                 ##   ###########                  ##                  ##   ##     ##   ##
#         ###   ##                 #    ##       ##          ##################          ##   #########   ##
#         ##    ###               ##    ###########          ##################          ##   ##     ##   ##
#        ###     ###              ##    ###########                  ##                  ##   ##     ##   ##
#      ####       ####           ###    ##       ##                  ##                  ##   #########   ##
#     ####         #####        ######                               ##                  ##   #########   ##
#  ######           #####      ### ########    #######    ########################       ##               ##
#  ####              ###       ##    ################     ########################       ##            #####
#   ##                ##                 ############     ########################      ###             ###





"""随机号码生成：01-35 之间，每组至少 5 个，组内不重复"""

import datetime
import random


def gen_numbers(count=5, min_num=1, max_num=35, rng=None):
    """随机生成一组号码。

    参数:
        count:   每组号码个数（默认 5，可传更大值，上限 35）
        min_num: 号码下界（默认 1）
        max_num: 号码上界（默认 35）
        rng:     随机源。不传用全局 random；传入 random.Random 实例则独立可复现，
                 不会影响进程内其他 random 用法

    返回:
        list[str]: 补零两位的号码列表，如 ['03', '11', '17', '26', '35']
    """
    if not (1 <= count <= max_num - min_num + 1):
        raise ValueError("count 超出可取的不重复号码数量范围")
    if rng is None:
        rng = random
    nums = rng.sample(range(min_num, max_num + 1), count)   # sample 保证不重复
    return [f"{n:02d}" for n in sorted(nums)]                # 补零 + 从小到大


def gen_ticket(front_count=5, back_count=2, seed=None):
    """生成一注完整号码：前区 01-35 取 5 个 + 后区 01-12 取 2 个，各自组内不重复。

    参数:
        seed: 随机种子。传入时同一 seed 必得同一注号码（前区+后区一起可复现）；
              不传则纯随机。种子只作用于本函数内的独立随机实例，不污染全局。

    返回:
        dict: {"front": [...前区号码], "back": [...后区号码]}
    """
    rng = random.Random(seed)
    return {
        "front": gen_numbers(count=front_count, min_num=1, max_num=35, rng=rng),
        "back": gen_numbers(count=back_count, min_num=1, max_num=12, rng=rng),
    }


# 大乐透开奖日：周一 / 周三 / 周六（date.weekday(): 0=周一, 2=周三, 5=周六）
DRAW_WEEKDAYS = (0, 2, 5)


def next_draw_date(date):
    """返回 date 所属期的开奖日（含当天：当天开奖则返回当天本身）。

    大乐透周一/三/六开奖，归期规则：
        周二跑 -> 归到周三那期
        周五跑 -> 归到周六那期
        周日跑 -> 归到下周一那期
    同一期开奖周期内任意一天跑，归到的都是同一期开奖日。
    """
    for delta in range(7):
        d = date + datetime.timedelta(days=delta)
        if d.weekday() in DRAW_WEEKDAYS:
            return d


def gen_daily_tickets(n=5, date=None, by_draw=True):
    """生成某天对应的 n 注号码。

    种子 = 归期日期(YYYYMMDD) * 100 + 序号：
      - 同一周期内重复运行 -> n 注号码完全一致（可复现，"本期幸运号"可分享）
      - 各注种子不同        -> 注与注之间号码不重复
      - 跨期               -> 归期日期变化，号码自动更新

    参数:
        n:       注数（默认 5，上限 99——种子尾部两位）
        date:    datetime.date；不传默认今天，传日期可回算任意一天
        by_draw: True(默认)按【期】固定——种子用本期开奖日（周一/三/六），
                 开奖周期内任意一天跑，号码都一致；
                 False 按自然日固定（每天一组）

    返回:
        list[dict]: [{front, back}, ...]
    """
    if not (1 <= n <= 99):
        raise ValueError("n 取值范围 1~99")
    if date is None:
        date = datetime.date.today()
    seed_date = next_draw_date(date) if by_draw else date
    base = int(seed_date.strftime("%Y%m%d"))
    return [gen_ticket(seed=base * 100 + i) for i in range(1, n + 1)]


if __name__ == "__main__":
    today = datetime.date.today()
    draw = next_draw_date(today)
    weekday_cn = "周" + "一二三四五六日"[draw.weekday()]
    print("=== 今日 {} 幸运号码（本期开奖日: {} {}，本期内号码固定）===".format(
        today.isoformat(), draw.isoformat(), weekday_cn))
    for i, ticket in enumerate(gen_daily_tickets(10), start=1):
        print("第{}组: 前区 {} + 后区 {}".format(
            i, " ".join(ticket["front"]), " ".join(ticket["back"])))
        

