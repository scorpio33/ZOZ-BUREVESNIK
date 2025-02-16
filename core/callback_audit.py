from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class CallbackInfo:
    callback_data: str
    menu_location: str
    handler_exists: bool
    handler_path: Optional[str] = None

class CallbackAudit:
    def __init__(self):
        self.callbacks: Dict[str, CallbackInfo] = {}
        
    def register_callback(self, callback_data: str, menu_location: str, handler_exists: bool, handler_path: Optional[str] = None):
        self.callbacks[callback_data] = CallbackInfo(
            callback_data=callback_data,
            menu_location=menu_location,
            handler_exists=handler_exists,
            handler_path=handler_path
        )

    def get_missing_handlers(self) -> List[str]:
        return [cb for cb, info in self.callbacks.items() if not info.handler_exists]

    def generate_report(self) -> str:
        report = ["=== Callback Audit Report ===\n"]
        
        # Существующие обработчики
        report.append("\n✅ Implemented Callbacks:")
        for cb, info in self.callbacks.items():
            if info.handler_exists:
                report.append(f"- {cb} ({info.menu_location}) → {info.handler_path}")
        
        # Отсутствующие обработчики
        report.append("\n❌ Missing Handlers:")
        for cb, info in self.callbacks.items():
            if not info.handler_exists:
                report.append(f"- {cb} ({info.menu_location})")
        
        return "\n".join(report)