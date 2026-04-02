from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _normalize_front(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if "://" in text:
        return text
    return f"tcp://{text}"


def _looks_like_app_id(value: Any) -> bool:
    text = str(value or "").strip().lower()
    return text.startswith("client_")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    return text in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class CtpExecutionGuardrails:
    enabled: bool = False
    allowed_instruments: list[str] = field(default_factory=list)
    max_order_qty: int = 0
    max_net_position: int = 0
    max_submit_per_minute: int = 0
    price_mode: str = "best_level_1"
    allow_live_order_smoke: bool = False

    @classmethod
    def from_dict(cls, values: dict[str, Any] | None) -> "CtpExecutionGuardrails":
        payload = values or {}

        def _first(*keys: str, default: Any = "") -> Any:
            for key in keys:
                if key in payload and payload[key] is not None:
                    return payload[key]
            return default

        instruments = _first("allowed_instruments", "AllowedInstruments", default=[])
        return cls(
            enabled=_as_bool(_first("enabled", "Enabled", default=False)),
            allowed_instruments=[str(item) for item in instruments],
            max_order_qty=int(_first("max_order_qty", "MaxOrderQty", default=0) or 0),
            max_net_position=int(_first("max_net_position", "MaxNetPosition", default=0) or 0),
            max_submit_per_minute=int(
                _first("max_submit_per_minute", "MaxSubmitPerMinute", default=0) or 0
            ),
            price_mode=str(_first("price_mode", "PriceMode", default="best_level_1")),
            allow_live_order_smoke=_as_bool(
                _first("allow_live_order_smoke", "AllowLiveOrderSmoke", default=False)
            ),
        )

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.enabled:
            return issues
        if not self.allowed_instruments:
            issues.append("execution_guardrails.allowed_instruments")
        if self.max_order_qty <= 0:
            issues.append("execution_guardrails.max_order_qty")
        if self.max_net_position <= 0:
            issues.append("execution_guardrails.max_net_position")
        if self.max_submit_per_minute <= 0:
            issues.append("execution_guardrails.max_submit_per_minute")
        if self.price_mode != "best_level_1":
            issues.append("execution_guardrails.price_mode")
        return issues


@dataclass(slots=True)
class CtpAdapterConfig:
    broker_id: str = ""
    user_id: str = ""
    password: str = ""
    auth_code: str = ""
    app_id: str = ""
    md_front: str = ""
    td_front: str = ""
    product_info: str = ""
    client_id: int = 0
    provider_id: int = 0
    post_login_delay_seconds: int = 0
    native_pack_dir: str = ""
    managed_assembly_dir: str = ""
    instruments: list[str] = field(default_factory=list)
    execution_guardrails: CtpExecutionGuardrails = field(default_factory=CtpExecutionGuardrails)

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "CtpAdapterConfig":
        def _first(*keys: str, default: Any = "") -> Any:
            for key in keys:
                if key in values and values[key] is not None:
                    return values[key]
            return default

        instruments = _first("instruments", "Instruments", default=[])
        chinese_product_name = _first("产品名称", default="")
        explicit_app_id = _first("app_id", "AppID", default="")
        app_id_value = explicit_app_id
        if not app_id_value and _looks_like_app_id(chinese_product_name):
            app_id_value = chinese_product_name

        product_info_value = _first("product_info", "ProductInfo", "service", "Service", default="")
        if not product_info_value and chinese_product_name and not _looks_like_app_id(chinese_product_name):
            product_info_value = chinese_product_name

        execution_guardrails = CtpExecutionGuardrails.from_dict(
            _first("execution_guardrails", "ExecutionGuardrails", default={})
        )

        return cls(
            broker_id=str(_first("broker_id", "BrokerID", "经纪商代码")),
            user_id=str(_first("user_id", "UserID", "用户名")),
            password=str(_first("password", "Password", "密码")),
            auth_code=str(_first("auth_code", "AuthCode", "授权编码")),
            app_id=str(app_id_value),
            md_front=_normalize_front(_first("md_front", "Pricer", "行情服务器")),
            td_front=_normalize_front(_first("td_front", "Host", "交易服务器")),
            product_info=str(product_info_value),
            client_id=int(_first("client_id", "ClientID", default=0) or 0),
            provider_id=int(_first("provider_id", "ProviderId", default=0) or 0),
            post_login_delay_seconds=int(
                _first("post_login_delay_seconds", "PostLoginDelaySeconds", default=0) or 0
            ),
            native_pack_dir=str(_first("native_pack_dir", "NativePackDir")),
            managed_assembly_dir=str(_first("managed_assembly_dir", "ManagedAssemblyDir")),
            instruments=[str(item) for item in instruments],
            execution_guardrails=execution_guardrails,
        )

    @classmethod
    def from_json_file(cls, path: str | Path) -> "CtpAdapterConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("CTP config file must contain a JSON object")
        return cls.from_dict(payload)

    @classmethod
    def from_env(cls, prefix: str = "NAUTILUS_CTP_") -> "CtpAdapterConfig":
        def _env(name: str, default: str = "") -> str:
            return os.environ.get(f"{prefix}{name}", default)

        instruments_raw = _env("INSTRUMENTS")
        instruments = [item.strip() for item in instruments_raw.split(",") if item.strip()]
        guardrail_instruments_raw = _env("EXECUTION_ALLOWED_INSTRUMENTS")
        guardrail_instruments = [
            item.strip() for item in guardrail_instruments_raw.split(",") if item.strip()
        ]
        return cls(
            broker_id=_env("BROKER_ID"),
            user_id=_env("USER_ID"),
            password=_env("PASSWORD"),
            auth_code=_env("AUTH_CODE"),
            app_id=_env("APP_ID"),
            md_front=_env("MD_FRONT"),
            td_front=_env("TD_FRONT"),
            product_info=_env("PRODUCT_INFO"),
            client_id=int(_env("CLIENT_ID", "0") or 0),
            provider_id=int(_env("PROVIDER_ID", "0") or 0),
            post_login_delay_seconds=int(_env("POST_LOGIN_DELAY_SECONDS", "0") or 0),
            native_pack_dir=_env("NATIVE_PACK_DIR"),
            managed_assembly_dir=_env("MANAGED_ASSEMBLY_DIR"),
            instruments=instruments,
            execution_guardrails=CtpExecutionGuardrails(
                enabled=_as_bool(_env("EXECUTION_GUARDRAILS_ENABLED", "")),
                allowed_instruments=guardrail_instruments,
                max_order_qty=int(_env("EXECUTION_MAX_ORDER_QTY", "0") or 0),
                max_net_position=int(_env("EXECUTION_MAX_NET_POSITION", "0") or 0),
                max_submit_per_minute=int(_env("EXECUTION_MAX_SUBMIT_PER_MINUTE", "0") or 0),
                price_mode=_env("EXECUTION_PRICE_MODE", "best_level_1"),
                allow_live_order_smoke=_as_bool(_env("EXECUTION_ALLOW_LIVE_ORDER_SMOKE", "")),
            ),
        )

    def validate(self) -> list[str]:
        missing: list[str] = []
        required_pairs = {
            "broker_id": self.broker_id,
            "user_id": self.user_id,
            "password": self.password,
            "md_front": self.md_front,
            "td_front": self.td_front,
        }
        for field_name, value in required_pairs.items():
            if not value:
                missing.append(field_name)
        if not self.instruments:
            missing.append("instruments")
        missing.extend(self.execution_guardrails.validate())
        return missing
