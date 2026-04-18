import requests
from datetime import datetime
import os
import html

API_URL = "https://www.881903.com/api/live/toolbar"

channels = {
    "1": {"id": "881", "name": "商業電台 881"},
    "2": {"id": "903", "name": "商業電台 903"},
    "3": {"id": "864", "name": "AM864"},
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.881903.com/",
}

resp = requests.get(API_URL, headers=headers, timeout=10)

if resp.status_code != 200:
    print("请求失败:", resp.status_code)
    exit()

try:
    data = resp.json()
except:
    print("不是JSON，被挡了")
    print(resp.text[:200])
    exit()

timetable_all = data["response"]["channelTimetableList"]

xml_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<tv>'
]

# channel
for ch in channels.values():
    xml_lines.append(f'  <channel id="{ch["id"]}">')
    xml_lines.append(f'    <display-name>{html.escape(ch["name"])}</display-name>')
    xml_lines.append('  </channel>')

# programme
for key, programs in timetable_all.items():
    if key not in channels:
        continue

    ch_id = channels[key]["id"]

    for prog in programs:
        start = datetime.strptime(prog["start_datetime"], "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(prog["end_datetime"], "%Y-%m-%d %H:%M:%S")

        start_str = start.strftime("%Y%m%d%H%M%S") + " +0800"
        end_str = end.strftime("%Y%m%d%H%M%S") + " +0800"

        title = html.escape(prog.get("program_name", ""))
        desc = html.escape(prog.get("host_name", ""))

        xml_lines.append(
            f'  <programme start="{start_str}" stop="{end_str}" channel="{ch_id}">'
        )
        xml_lines.append(f'    <title lang="zh_HK">{title}</title>')

        if desc:
            xml_lines.append(f'    <desc>{desc}</desc>')

        xml_lines.append('  </programme>')

xml_lines.append('</tv>')

with open("epg.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(xml_lines))

print("epg.xml 已生成")
