#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CtpEventKind {
    Connected,
    Disconnected,
    AuthSucceeded,
    AuthFailed,
    LoginSucceeded,
    LoginFailed,
    SettlementConfirmed,
    Tick,
    Order,
    Trade,
    Position,
    Account,
    Instrument,
    InstrumentStatus,
    Error,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CtpEvent {
    pub kind: CtpEventKind,
    pub venue_symbol: Option<String>,
    pub exchange_id: Option<String>,
    pub client_order_id: Option<String>,
    pub request_id: Option<String>,
    pub message: Option<String>,
}
