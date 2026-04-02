use std::collections::BTreeSet;

use crate::commands::{CtpCommand, CtpCommandKind};

fn subscription_key(venue_symbol: &Option<String>, exchange_id: &Option<String>) -> Option<String> {
    match (venue_symbol.as_deref(), exchange_id.as_deref()) {
        (Some(symbol), Some(exchange)) => Some(format!("{exchange}:{symbol}")),
        (Some(symbol), None) => Some(symbol.to_owned()),
        _ => None,
    }
}

#[derive(Debug, Clone, Default)]
pub struct CtpMarketRuntime {
    subscriptions: BTreeSet<String>,
}

impl CtpMarketRuntime {
    pub fn on_command(&mut self, command: &CtpCommand) {
        let Some(key) = subscription_key(&command.venue_symbol, &command.exchange_id) else {
            return;
        };

        match command.kind {
            CtpCommandKind::SubscribeMarketData => {
                self.subscriptions.insert(key);
            }
            CtpCommandKind::UnsubscribeMarketData => {
                self.subscriptions.remove(&key);
            }
            _ => {}
        }
    }

    pub fn subscription_count(&self) -> usize {
        self.subscriptions.len()
    }

    pub fn is_subscribed(&self, venue_symbol: &str, exchange_id: Option<&str>) -> bool {
        let key = match exchange_id {
            Some(exchange) => format!("{exchange}:{venue_symbol}"),
            None => venue_symbol.to_owned(),
        };
        self.subscriptions.contains(&key)
    }
}
