from prettytable import from_csv
from PIL import Image,ImageFont,ImageDraw
from prettytable import from_csv,PrettyTable
_font =r'D:\desktop\code\jdbot\bot\font\msyh.ttf'
IN = r'D:\desktop\code\jdbot\bean_income.csv'
OUT =r'D:\desktop\code\jdbot\bean_outlay.csv'
TOTAL=r'D:\desktop\code\jdbot\bean_total.csv'

files = {"BEANIN":IN,"BEANOUT":OUT,"TOTAL":TOTAL}
tb = PrettyTable()
columns=[]
with open(files["BEANIN"],'r',encoding='utf-8') as f:
    lines = f.readlines()
lines = lines[-7:]
for line in lines:
    columns.append(line.split(',')[0])
tb.add_column('DATE',columns)
for key,file in files.items():
    columns = []
    with open(file,'r',encoding='utf-8') as f:
        lines = f.readlines()
    lines = lines[-7:]
    for line in lines:
        columns.append(line.split(',')[int(3)])
    tb.add_column(key,columns)
length = 172 + 100 * 3
im = Image.new("RGB", (length, 280), (244, 244, 244))
dr = ImageDraw.Draw(im)
font = ImageFont.truetype(_font, 18)
dr.text((10, 5), str(tb), font=font, fill="#000000")
im.show()
#     tb.add_column(creat_beanimg(file,'COUNT'+str(3),False))
# creat_beanimg(None,0,True,tb)
