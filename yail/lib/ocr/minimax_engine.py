import re
import json
import aiohttp
from typing import Dict

from conf.dev import OPENAI_API_KEY
from .base import OCREngine


VLM_API_HOST = "https://api.minimaxi.com"


async def call_vision(image_base64: str, prompt: str) -> str:
    """调用 MiniMax VLM API"""
    if image_base64.startswith('data:'):
        image_url = image_base64
    else:
        image_url = f"data:image/jpeg;base64,{image_base64}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{VLM_API_HOST}/v1/coding_plan/vlm",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                    "MM-API-Source": "Minimax-MCP"
                },
                json={
                    "prompt": prompt,
                    "image_url": image_url
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                data = await resp.json()
                if data.get("base_resp", {}).get("status_code") != 0:
                    raise Exception(f"VLM API error: {data.get('base_resp')}")
                return data.get("content", "")
    except Exception as e:
        raise Exception(f"VLM API call failed: {str(e)}")


class MiniMaxOCREngine(OCREngine):
    """MiniMax VLM API 引擎实现"""
    
    async def recognize_driving_license(self, image_base64: str) -> Dict[str, str]:
        """
        识别行驶证
        
        Args:
            image_base64: base64 编码的图片
            
        Returns:
            包含 name, carNo, brand, model, regDate 的字典
        """
        prompt = (
            "从行驶证图片中提取：姓名、车牌号、车辆品牌、型号、注册日期。"
            "只返回JSON格式：{\"name\":\"\",\"carNo\":\"\",\"brand\":\"\",\"model\":\"\",\"regDate\":\"\"}"
        )
        
        content = await call_vision(image_base64, prompt)
        
        if not content:
            raise Exception("Empty response from VLM API")
        
        # 去除 markdown 代码块
        json_str = re.sub(r'```json\n?|```\n?', '', content).strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parse error: {str(e)}, content: {content[:200]}")
    
    async def recognize_driver_license(self, image_base64: str) -> Dict[str, str]:
        """
        识别驾驶证
        
        Args:
            image_base64: base64 编码的图片
            
        Returns:
            包含 name 的字典
        """
        prompt = (
            "从驾驶证图片中提取：姓名。"
            "只返回JSON格式：{\"name\":\"\"}"
        )
        
        content = await call_vision(image_base64, prompt)
        
        if not content:
            raise Exception("Empty response from VLM API")
        
        # 去除 markdown 代码块
        json_str = re.sub(r'```json\n?|```\n?', '', content).strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parse error: {str(e)}, content: {content[:200]}")
