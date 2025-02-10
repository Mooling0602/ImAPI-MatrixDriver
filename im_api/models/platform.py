from enum import Enum

class Platform(Enum):
    """平台类型"""
    MINECRAFT = "minecraft"
    QQ = "qq"
    KOOK = "kook"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    MATRIX = "matrix"
    
    @classmethod
    def from_string(cls, value: str) -> 'Platform':
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Unknown platform: {value}")

# 导出
__all__ = ["Platform"] 