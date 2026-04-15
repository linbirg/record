from .base import OCREngine
from .paddleocr_engine import PaddleOCREngine
from .minimax_engine import MiniMaxOCREngine


def create_ocr_engine(engine: str = None) -> OCREngine:
    """
    工厂函数：根据参数或配置创建 OCR 引擎
    
    Args:
        engine: 引擎名称，可选值 "paddleocr", "minimax"。如果为 None，则使用配置文件中的 OCR_ENGINE
    
    Returns:
        OCREngine 实例
    """
    from conf.dev import OCR_ENGINE
    
    engine = engine or OCR_ENGINE
    
    if engine == "paddleocr":
        return PaddleOCREngine()
    elif engine == "minimax":
        return MiniMaxOCREngine()
    else:
        raise ValueError(f"Unknown OCR engine: {engine}. Available options: paddleocr, minimax")


__all__ = ['OCREngine', 'PaddleOCREngine', 'MiniMaxOCREngine', 'create_ocr_engine']
