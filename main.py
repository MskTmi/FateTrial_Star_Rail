import json
import requests
import logging

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, register
from astrbot.api.message_components import Image, Plain

@register("Star_Rail", "FateTrial", "崩坏星穹铁道攻略查询插件", "1.0.0")
class StrategyQuery(Star):
    @filter.command("崩铁查询")
    async def query_strategy(self, event: AstrMessageEvent, *, message: str):
        yield event.plain_result("正在查询攻略，请稍候...")

        url = f'https://api.yaohud.cn/api/v5/mihoyou/xing?key=SqGWZxWJxEWagRFxkqB&msg={message}'
        try:
            response = requests.post(url, data={'key1': 'value1', 'key2': 'value2'})
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                logging.error(f"JSON 解析失败: {e}")
                yield event.plain_result(f"数据解析失败，原始响应：\n{response.text}")
                return

            # 安全获取字段，若缺失则显示 "无"
            name = result.get('name', '无')
            icon = result.get('icon', '无')
            take = result.get('take', '无')

            guangzhui = result.get('guangzhui_tuijian', [])
            cones = [c.get('name', '无') for c in guangzhui] or ['无']

            rec = result.get('recommendation', {}) or result.get('yq_tuijian', {})
            early_one = rec.get('one', {}).get('early', '无')
            early_two = rec.get('two', {}).get('early', '无')

            zhuct = result.get('zhuct') or result.get('zhuangbei_tuijian', {})
            qu = zhuct.get('qu', '无')
            jiao = zhuct.get('jiao', '无')
            wei = zhuct.get('wei', '无')
            lian = zhuct.get('lian', '无')

            fuct = result.get('fuct', '无')
            bytion = result.get('bytion', '无')
            tips = result.get('tips', '无')
            image_url = result.get('picture')

            teams = []
            if 'ranks1' in result:
                ranks_keys = ['ranks', 'ranks1']
            else:
                ranks_keys = ['peidui_tuijian']

            for key in ranks_keys:
                grp = result.get(key, {})
                name_t = grp.get('name', '无')
                ids = grp.get('idstext', '无')
                coll = grp.get('collocation', '无')
                teams.append((name_t, ids, coll))

            content_lines = [
                f"⭐ 角色攻略：{name} ⭐\n",
                f"🖼️ 角色简介：\n{icon}\n",
                f"🎯 获取途径：{take}\n",
                f"💫 光锥推荐：{' '.join(cones)}\n",
                f"🔮 遗器推荐：{early_one} + {early_two}\n",
                "📊 遗器词条：",
                f"躯干：{qu}",
                f"脚步：{jiao}",
                f"位面球：{wei}",
                f"连接绳：{lian}\n",
                f"💠 主词条优先级：{fuct}\n",
                "🤝 配队推荐：\n"
            ]

            for idx, (n, ids, coll) in enumerate(teams, start=1):
                content_lines.append(f"{idx}️⃣ {n}")
                content_lines.append(f"阵容：{ids}")
                content_lines.append(f"说明：{coll}\n")

            content_lines += [
                f"💡 遗器说明：\n{bytion}\n",
                f"📝 数据来源：{tips}"
            ]

            formatted_msg = "\n".join(content_lines)

            components = []
            if image_url:
                components.append(Image.fromURL(image_url))
            components.append(Plain(formatted_msg))
            yield event.chain_result(components)

        except requests.RequestException as e:
            logging.error(f"请求失败: {e}")
            yield event.plain_result(f"网络请求失败，请稍后重试。错误信息：{e}")
