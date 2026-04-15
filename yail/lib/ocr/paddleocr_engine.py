import re
import base64
import numpy as np
from typing import Dict, List
from io import BytesIO
from PIL import Image

from .base import OCREngine
from lib import logger


def decode_base64_image(img_str: str) -> np.ndarray:
    if img_str.startswith('data:'):
        img_str = img_str.split(',')[1]
    img_data = base64.b64decode(img_str)
    img = Image.open(BytesIO(img_data))
    return np.array(img)


class PaddleOCREngine(OCREngine):
    def __init__(self):
        from paddleocr import PaddleOCR
        import os
        os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
        
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            use_gpu=False,
            show_log=False
        )
        
        self.license_plate_pattern = re.compile(
            r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领]'
            r'[A-Z]'
            r'[A-Z0-9]{5,6}'
        )
        
        self.date_pattern = re.compile(
            r'(\d{4})年(\d{1,2})月(\d{1,2})日|'
            r'(\d{4})-(\d{1,2})-(\d{1,2})|'
            r'(\d{4})(\d{2})(\d{2})'
        )
        
        self.chinese_name_pattern = re.compile(r'^[\u4e00-\u9fa5]{2,4}$')
        self.brand_with_pai_pattern = re.compile(r'^([\u4e00-\u9fa5]+)牌(.+)$')
    
    def _parse_lines(self, ocr_result) -> List[Dict]:
        text_lines = []
        for line in ocr_result:
            if line is None:
                continue
            for item in line:
                if item is None or len(item) < 2:
                    continue
                text = item[1][0] if isinstance(item[1], tuple) else item[1]
                confidence = item[1][1] if isinstance(item[1], tuple) and len(item[1]) > 1 else 0
                text_lines.append({'text': text.strip(), 'confidence': confidence})
        return text_lines
    
    def _find_by_keyword_next_line(self, lines: List[Dict], keyword: str, next_n: int = 3) -> str:
        for i, line in enumerate(lines):
            if keyword in line['text']:
                for j in range(1, min(next_n + 1, len(lines) - i)):
                    next_text = lines[i + j]['text'].strip()
                    next_text_clean = re.sub(r'[:：\s]', '', next_text)
                    if next_text_clean:
                        date_match = self.date_pattern.search(next_text_clean)
                        if date_match:
                            if date_match.group(1):
                                return f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}"
                            elif date_match.group(4):
                                return f"{date_match.group(4)}-{int(date_match.group(5)):02d}-{int(date_match.group(6)):02d}"
                            elif date_match.group(7):
                                return f"{date_match.group(7)}-{date_match.group(8)}-{date_match.group(9)}"
                        if len(next_text_clean) >= 2:
                            return next_text_clean
                current_clean = line['text'].replace(keyword, '').strip()
                current_clean = re.sub(r'[:：\s]', '', current_clean)
                if current_clean and len(current_clean) >= 2:
                    return current_clean
        return ''
    
    def _split_brand_model(self, text: str) -> tuple:
        brand_match = re.match(r'^([\u4e00-\u9fa5]+)', text)
        if brand_match:
            return brand_match.group(1), text[len(brand_match.group(1)):]
        return text, ''
    
    def _extract_fields(self, lines: List[Dict]) -> Dict[str, str]:
        result = {'name': '', 'carNo': '', 'brand': '', 'model': '', 'regDate': ''}
        
        for line in lines:
            if not result['carNo']:
                plate_match = self.license_plate_pattern.search(line['text'])
                if plate_match:
                    result['carNo'] = plate_match.group()
                    logger.LOG_INFO("  -> 找到车牌号: %s", result['carNo'])
        
        name_candidates = []
        for i, line in enumerate(lines):
            if result['name']:
                break
            if '所有人' in line['text'] or '车主' in line['text']:
                for j in range(1, 5):
                    if i + j < len(lines):
                        cand = lines[i + j]['text'].strip()
                        cand_clean = re.sub(r'[:：\s]', '', cand)
                        if self.chinese_name_pattern.match(cand_clean):
                            result['name'] = cand_clean
                            logger.LOG_INFO("  -> 找到姓名(所有人): %s", result['name'])
                            break
                if not result['name']:
                    current = re.sub(r'[:：\s]', '', line['text'].replace('所有人', '').replace('车主', ''))
                    if self.chinese_name_pattern.match(current):
                        result['name'] = current
                        logger.LOG_INFO("  -> 找到姓名(所有人当前行): %s", result['name'])
        
        if not result['name']:
            name_blacklist = [
                '检验', '发证', '注册', '车牌', '号牌', '车辆', '类型', '品牌', '型号', '使用', '性质', '地址', '电话',
                '上海', '深圳', '北京', '广州', '杭州', '南京', '成都', '重庆', '天津', '西安', '武汉', '苏州', '郑州',
                '长沙', '青岛', '济南', '石家庄', '福州', '厦门', '宁波', '大连', '沈阳', '长春', '哈尔滨', '呼和浩特',
                '昆明', '贵阳', '南宁', '海口', '太原', '合肥', '南昌', '兰州', '银川', '西宁', '乌鲁木齐', '拉萨',
                '省', '市', '区', '县', '路', '号', '室', '街', '道', '巷', '栋', '楼', '幢', '股份', '有限', '公司',
                '公安', '交通', '管理', '总队', '支队', '警察', '检验', '有效', '期间', '至', '日', '月', '年',
                '外', '内', '中', '东', '西', '南', '北', '发动机', '号码', '识别', '代号', 'VIN', 'vin',
                '备量', '整备', '质量', '外尺', '尺寸', '排量', '功率', '转速', '燃料', '种类', '轴', '轮',
                '进口', '国产', '海关', '关税', '商检', '登记', '证书', '凭证', '凭据', '副本', '正本', '中华人民共和国'
            ]
            for i, line in enumerate(lines):
                text = line['text'].strip()
                if len(text) >= 2 and len(text) <= 4 and self.chinese_name_pattern.match(text):
                    if text not in name_blacklist and not any(k in text for k in name_blacklist):
                        if not any(k in text for k in ['省', '市', '区', '县', '路', '号', '室', '街', '道', '巷', '栋', '楼', '幢']):
                            result['name'] = text
                            logger.LOG_INFO("  -> 找到姓名(候选): %s, pos=%d", text, i)
                            break
        
        for i, line in enumerate(lines):
            if '品牌型号' in line['text']:
                for j in range(1, 4):
                    if i + j < len(lines):
                        cand = lines[i + j]['text'].strip()
                        if cand and not self.date_pattern.match(cand):
                            brand, model = self._split_brand_model(cand)
                            if brand and model:
                                result['brand'] = brand
                                result['model'] = model
                                logger.LOG_INFO("  -> 找到品牌型号: %s / %s", brand, model)
                                break
                if not result['brand']:
                    current = line['text'].replace('品牌型号', '').strip()
                    if current:
                        brand, model = self._split_brand_model(current)
                        result['brand'] = brand
                        result['model'] = model
                        logger.LOG_INFO("  -> 找到品牌型号(当前行): %s / %s", brand, model)
        
        if not result['brand']:
            for i, line in enumerate(lines):
                text = line['text'].strip()
                match = self.brand_with_pai_pattern.match(text)
                if match:
                    result['brand'] = match.group(1)
                    result['model'] = match.group(2)
                    logger.LOG_INFO("  -> 找到品牌型号(牌匹配): %s / %s", result['brand'], result['model'])
                    break
        
        for i, line in enumerate(lines):
            if '注册日期' in line['text']:
                for j in range(1, 4):
                    if i + j < len(lines):
                        cand = lines[i + j]['text'].strip()
                        cand_clean = re.sub(r'[:：\s]', '', cand)
                        date_match = self.date_pattern.match(cand_clean)
                        if date_match:
                            if date_match.group(1):
                                result['regDate'] = f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}"
                            elif date_match.group(4):
                                result['regDate'] = f"{date_match.group(4)}-{int(date_match.group(5)):02d}-{int(date_match.group(6)):02d}"
                            elif date_match.group(7):
                                result['regDate'] = f"{date_match.group(7)}-{date_match.group(8)}-{date_match.group(9)}"
                            logger.LOG_INFO("  -> 找到注册日期: %s", result['regDate'])
                            break
        
        if not result['regDate']:
            for i, line in enumerate(lines):
                if '发证日期' in line['text']:
                    for j in range(1, 4):
                        if i + j < len(lines):
                            cand = lines[i + j]['text'].strip()
                            cand_clean = re.sub(r'[:：\s]', '', cand)
                            date_match = self.date_pattern.match(cand_clean)
                            if date_match:
                                if date_match.group(1):
                                    result['regDate'] = f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}"
                                elif date_match.group(4):
                                    result['regDate'] = f"{date_match.group(4)}-{int(date_match.group(5)):02d}-{int(date_match.group(6)):02d}"
                                elif date_match.group(7):
                                    result['regDate'] = f"{date_match.group(7)}-{date_match.group(8)}-{date_match.group(9)}"
                                logger.LOG_INFO("  -> 找到发证日期(备用): %s", result['regDate'])
                                break
        
        return result
    
    async def recognize_driving_license(self, image_base64: str) -> Dict[str, str]:
        img = decode_base64_image(image_base64)
        
        logger.LOG_INFO("开始 PaddleOCR 行驶证识别")
        ocr_result = self.ocr.ocr(img, cls=True)
        
        lines = self._parse_lines(ocr_result)
        
        logger.LOG_INFO("OCR 识别出 %d 行文本:", len(lines))
        for i, line in enumerate(lines):
            logger.LOG_INFO("  [%d] '%s' (conf=%.2f)", i, line['text'], line['confidence'])
        
        result = self._extract_fields(lines)
        logger.LOG_INFO("行驶证识别最终结果: %s", str(result))
        return result
    
    async def recognize_driver_license(self, image_base64: str) -> Dict[str, str]:
        img = decode_base64_image(image_base64)
        
        logger.LOG_INFO("开始 PaddleOCR 驾驶证识别")
        ocr_result = self.ocr.ocr(img, cls=True)
        
        lines = self._parse_lines(ocr_result)
        
        logger.LOG_INFO("驾驶证 OCR 识别出 %d 行文本:", len(lines))
        for i, line in enumerate(lines):
            logger.LOG_INFO("  [%d] '%s' (conf=%.2f)", i, line['text'], line['confidence'])
        
        result = {'name': ''}
        
        for i, line in enumerate(lines):
            if '姓名' in line['text']:
                for j in range(1, 4):
                    if i + j < len(lines):
                        cand = lines[i + j]['text'].strip()
                        cand_clean = re.sub(r'[:：\s]', '', cand)
                        if self.chinese_name_pattern.match(cand_clean):
                            result['name'] = cand_clean
                            logger.LOG_INFO("  -> 找到姓名: %s", result['name'])
                            break
                if not result['name']:
                    current = re.sub(r'[:：\s]', '', line['text'].replace('姓名', ''))
                    if self.chinese_name_pattern.match(current):
                        result['name'] = current
                        logger.LOG_INFO("  -> 找到姓名(当前行): %s", result['name'])
                break
        
        if not result['name']:
            name_blacklist = [
                '检验', '发证', '注册', '车牌', '号牌', '车辆', '类型', '品牌', '型号', '使用', '性质', '地址', '电话',
                '上海', '深圳', '北京', '广州', '杭州', '南京', '成都', '重庆', '天津', '西安', '武汉', '苏州', '郑州',
                '长沙', '青岛', '济南', '石家庄', '福州', '厦门', '宁波', '大连', '沈阳', '长春', '哈尔滨', '呼和浩特',
                '省', '市', '区', '县', '路', '号', '室', '街', '道', '巷', '栋', '楼', '幢', '股份', '有限', '公司',
                '公安', '交通', '管理', '总队', '支队', '警察', '有效', '期间', '至', '日', '月', '年', '中华人民共和国'
            ]
            for i, line in enumerate(lines):
                text = line['text'].strip()
                if len(text) >= 2 and len(text) <= 4 and self.chinese_name_pattern.match(text):
                    if text not in name_blacklist and not any(k in text for k in name_blacklist):
                        if not any(k in text for k in ['省', '市', '区', '县', '路', '号', '室', '街', '道', '巷', '栋', '楼', '幢']):
                            result['name'] = text
                            logger.LOG_INFO("  -> 找到姓名(候选): %s", text)
                            break
        
        logger.LOG_INFO("驾驶证识别最终结果: %s", str(result))
        return result
