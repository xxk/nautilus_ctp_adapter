use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CtpCommandKind {
    Connect,
    Disconnect,
    SubscribeMarketData,
    UnsubscribeMarketData,
    SubmitOrder,
    CancelOrder,
    ReplaceOrder,
    QueryInstruments,
    QueryPositions,
    QueryAccount,
    QueryInstrumentStatus,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CtpCommand {
    pub kind: CtpCommandKind,
    pub venue_symbol: Option<String>,
    pub exchange_id: Option<String>,
    pub client_order_id: Option<String>,
    pub request_id: Option<String>,
    pub payload: HashMap<String, String>,
}
