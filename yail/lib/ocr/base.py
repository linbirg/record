from abc import ABC, abstractmethod
from typing import Dict


class OCREngine(ABC):
    """OCR 引擎抽象基类"""
    
    @abstractmethod
    async def recognize_driving_license(self, image_base64: str) -> Dict[str, str]:
        """
        识别行驶证
        
        Args:
            image_base64: base64 编码的图片（可能带 data:image 前缀）
            
        Returns:
            包含识别结果的字典，包含以下字段：
            - name: 车主姓名
            - carNo: 车牌号
            - brand: 车辆品牌
            - model: 车辆型号
            - regDate: 注册日期
        """
        pass
    
    @abstractmethod
    async def recognize_driver_license(self, image_base64: str) -> Dict[str, str]:
        """
        识别驾驶证
        
        Args:
            image_base64: base64 编码的图片（可能带 data:image 前缀）
            
        Returns:
            包含识别结果的字典，包含以下字段：
            - name: 姓名
        """
        pass
