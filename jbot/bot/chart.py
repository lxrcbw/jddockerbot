from telethon import events
from .. import jdbot, chat_id, _LogDir, logger
import os
import re
from ..bot.quickchart import QuickChart

bean_log = _LogDir + '/jd_bean_change/'
_botimg = _LogDir + '/bot/bean.jpeg'


@jdbot.on(events.NewMessage(chats=chat_id, pattern=r'^/chart'))
async def mybean(event):
    try:
        await jdbot.send_message(chat_id, '正在查询，请稍后')
        if len(event.raw_text.split(' ')) > 1:
            text = event.raw_text.replace('/chart ', '')
        else:
            text = None
        if text and int(text):
            date, counts, beanins, beanouts, beantotals, redtotals = get_beans_data(
                int(text))
            creat_chart(date, counts[0][0], beanins,
                        beanouts, beantotals, redtotals[-1])
            await jdbot.send_message(chat_id, f'您的账号{text}收支情况', file=_botimg)
        else:
            await jdbot.send_message(chat_id, '请正确使用命令\n/chart n n为第n个账号')
    except Exception as e:
        await jdbot.send_message(chat_id, 'something wrong,I\'m sorry\n'+str(e))
        logger.error('something wrong,I\'m sorry'+str(e))


def get_beans_data(num):
    num = int(num) - 1
    files = os.listdir(bean_log)
    files.sort(reverse=True)
    dates = []
    counts = []
    redtotals = []
    beantotals = []
    beanouts = []
    beanins = []
    for file in files:
        with open(bean_log+'/'+file, 'r', encoding='utf-8') as f:
            lines = f.read()
        date = '-'.join(file.split('-')[1:3])
        if date in dates:
            continue
        count = re.compile('(?<=账号'+str(num+1)+'：)\S+')
        beanin = re.compile(r'(?<=昨日收入：)\d+')
        beanout = re.compile(r'(?<=昨日支出：)\S*\d+')
        beantotal = re.compile(r'(?<=当前京豆：)\d+')
        redtotal = re.compile(r'(?<=当前总红包：)\d+\.\d+')
        dates.insert(0, date)
        counts.insert(0, count.findall(lines))
        beanins.insert(0, beanin.findall(lines)[num])
        beanouts.insert(0, beanout.findall(lines)[num])
        beantotals.insert(0, beantotal.findall(lines)[num])
        redtotals.insert(0, redtotal.findall(lines)[num])
        if len(dates) == 7:
            break
    return dates, counts, astm(beanins), astm(beanouts), astm(beantotals), redtotals


def astm(arr):
    _arr = []
    for _ in arr:
        _arr.append(int(_.replace('-', '')))
    return _arr


def creat_chart(xdata, title, bardata, bardata2, linedate, otitle):
    qc = QuickChart()
    qc.background_color = '#fff'
    qc.width = "1000"
    qc.height = "600"
    qc.config = {
        "type": "bar",
        "data": {
            "labels": xdata,
            "datasets": [
                {
                    "label": "IN",
                    "backgroundColor": [
                        "rgb(255, 99, 132)",
                        "rgb(255, 159, 64)",
                        "rgb(255, 205, 86)",
                        "rgb(75, 192, 192)",
                        "rgb(54, 162, 235)",
                        "rgb(153, 102, 255)",
                        "rgb(255, 99, 132)"
                    ],
                    "yAxisID": "y1",
                    "data": bardata
                },
                {
                    "label": "OUT",
                    "backgroundColor": [
                        "rgb(255, 99, 132)",
                        "rgb(255, 159, 64)",
                        "rgb(255, 205, 86)",
                        "rgb(75, 192, 192)",
                        "rgb(54, 162, 235)",
                        "rgb(153, 102, 255)",
                        "rgb(255, 99, 132)"
                    ],
                    "yAxisID": "y1",
                    "data": bardata2
                },
                {
                    "label": "TOTAL",
                    "type": "line",
                    "fill": False,
                    "backgroundColor": "rgb(201, 203, 207)",
                    "yAxisID": "y2",
                    "data": linedate
                }
            ]
        },
        "options": {
            "plugins": {
                "datalabels": {
                    "anchor": 'end',
                    "align": -100,
                    "color": '#666',
                    "font": {
                        "size": 20,
                    }
                },
            },
            "legend": {
                "labels": {
                    "fontSize": 20,
                    "fontStyle": 'bold',
                }
            },
            "title": {
                "display": True,
                "text": title + "   IN OUT AND TOTAL",
                "fontSize": 24,
            },
            "scales": {
                "xAxes": [{
                    "ticks": {
                        "fontSize": 24,
                    }
                }],
                "yAxes": [
                    {
                        "id": "y1",
                        "type": "linear",
                        "display": False,
                        "position": "left",
                        "ticks": {
                            "max": int(int(max([max(bardata), max(bardata2)])+100)*2)
                        },
                        "scaleLabel": {
                            "fontSize": 20,
                            "fontStyle": 'bold',
                        }
                    },
                    {
                        "id": "y2",
                        "type": "linear",
                        "display": False,
                        "ticks": {
                            "min": int(min(linedate)*2-(max(linedate))-100),
                            "max": int(int(max(linedate)))
                        },
                        "position": "right"
                    }
                ]
            }
        }
    }
    qc.to_file(_botimg)
