from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REQUIRED_NATIVE_DLLS = (
    "ctp_native.dll",
    "thostmduserapi_se.dll",
    "thosttraderapi_se.dll",
)

BOOTSTRAP_MANAGED_DLLS = (
    "CTPProviderSwig.dll",
    "CTPProviderSwig.Core.dll",
    "iTrading.Core.dll",
    "iTradingQuant.dll",
)

OPTIONAL_COMPAT_DLLS = (
    "thostmduserapi.dll",
    "thosttraderapi.dll",
)

CTP_NATIVE_SCAFFOLD_NOT_IMPLEMENTED_CODE = -9000
CTP_NATIVE_INVALID_HANDLE_CODE = -9001
CTP_NATIVE_SCAFFOLD_NOT_IMPLEMENTED_MESSAGE = (
    "repo-owned ctp_native scaffold only; live vendor bridge not implemented"
)
CTP_NATIVE_INVALID_HANDLE_MESSAGE = (
    "function received a null or invalid repo-owned ctp_native session handle"
)


@dataclass(frozen=True, slots=True)
class CtpNativeExport:
    symbol: str
    area: str
    purpose: str


@dataclass(frozen=True, slots=True)
class CtpNativeErrorContract:
    name: str
    code: int
    message: str


REPO_OWNED_CTP_NATIVE_EXPORTS = (
    CtpNativeExport("MdCreate", "md", "Create the repository-owned market-data session handle."),
    CtpNativeExport("MdDispose", "md", "Release the market-data session handle and callbacks."),
    CtpNativeExport("MdInit", "md", "Initialize the MD front connection with a normalized front address."),
    CtpNativeExport("MdLogin", "md", "Start MD login with normalized broker/user/password/front inputs."),
    CtpNativeExport("MdLoginWithProductInfo", "md", "Start MD login with normalized broker/user/password and optional UserProductInfo."),
    CtpNativeExport("MdLoginWithCompatibility", "md", "Start MD login with optional SDK compatibility fields when a trusted local source provides them."),
    CtpNativeExport("MdSubscribe", "md", "Subscribe one or more symbols for market data."),
    CtpNativeExport("MdUnsubscribe", "md", "Remove one or more symbols from market-data subscription."),
    CtpNativeExport("MdSetCallback", "md", "Register the native tick callback."),
    CtpNativeExport("MdSetLoginCallback", "md", "Register the native MD login callback."),
    CtpNativeExport("MdSetFrontConnectedCallback", "md", "Register the native MD front-connected callback."),
    CtpNativeExport("MdSetFrontDisconnectedCallback", "md", "Register the native MD disconnect callback."),
    CtpNativeExport("TdCreate", "td", "Create the repository-owned trading session handle."),
    CtpNativeExport("TdDispose", "td", "Release the trading session handle and callbacks."),
    CtpNativeExport("TdInit", "td", "Initialize the TD front connection with a normalized front address."),
    CtpNativeExport("TdAuthenticate", "td", "Run TD authenticate using broker, user, auth code and AppID."),
    CtpNativeExport("TdLogin", "td", "Run TD login after authenticate succeeds."),
    CtpNativeExport("TdSetCallback", "td", "Register the normalized TD order/trade callback."),
    CtpNativeExport("TdSetLoginCallback", "td", "Register the normalized TD login callback."),
    CtpNativeExport("TdSetFrontDisconnectedCallback", "td", "Register the normalized TD disconnect callback."),
    CtpNativeExport("TdSetInstrumentCallback", "td", "Register the normalized instrument query callback."),
    CtpNativeExport("TdSetPositionCallback", "td", "Register the normalized position query callback."),
    CtpNativeExport("TdSetAccountCallback", "td", "Register the normalized account query callback."),
    CtpNativeExport("TdConfirmSettlement", "td", "Confirm settlement before live order flow starts."),
    CtpNativeExport("TdOrderSend", "td", "Submit a normalized order request to CTP."),
    CtpNativeExport("TdOrderAction", "td", "Cancel an existing order via normalized action request."),
    CtpNativeExport("TdQryInstrument", "query", "Query normalized instrument snapshots."),
    CtpNativeExport("TdQryPosition", "query", "Query normalized position snapshots."),
    CtpNativeExport("TdQryAccount", "query", "Query normalized account snapshots."),
    CtpNativeExport("TdQryInstrumentStatus", "query", "Query normalized instrument status snapshots."),
)

REPO_OWNED_CTP_NATIVE_ERROR_CONTRACTS = (
    CtpNativeErrorContract(
        "scaffold_not_implemented",
        CTP_NATIVE_SCAFFOLD_NOT_IMPLEMENTED_CODE,
        CTP_NATIVE_SCAFFOLD_NOT_IMPLEMENTED_MESSAGE,
    ),
    CtpNativeErrorContract(
        "invalid_handle",
        CTP_NATIVE_INVALID_HANDLE_CODE,
        CTP_NATIVE_INVALID_HANDLE_MESSAGE,
    ),
)


def describe_native_pack(base_dir: str | Path) -> dict[str, object]:
    root = Path(base_dir)
    return {
        "vendor_dir": root / "vendor" / "ctp",
        "bin_dir": root / "vendor" / "ctp" / "bin",
        "required_native_dlls": list(REQUIRED_NATIVE_DLLS),
        "managed_bootstrap_dlls": list(BOOTSTRAP_MANAGED_DLLS),
        "optional_compat_dlls": list(OPTIONAL_COMPAT_DLLS),
        "repo_owned_exports": [export.symbol for export in REPO_OWNED_CTP_NATIVE_EXPORTS],
        "repo_owned_error_contracts": [
            {
                "name": contract.name,
                "code": contract.code,
                "message": contract.message,
            }
            for contract in REPO_OWNED_CTP_NATIVE_ERROR_CONTRACTS
        ],
    }
