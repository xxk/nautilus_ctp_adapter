use std::collections::{HashMap, HashSet};

use crate::commands::{CtpCommand, CtpCommandKind};
use crate::events::{CtpEvent, CtpEventKind};

#[derive(Debug, Clone, PartialEq)]
pub struct CtpInstrumentRecord {
    pub venue_symbol: String,
    pub exchange_id: Option<String>,
    pub product_class: Option<String>,
    pub instrument_name: Option<String>,
    pub price_tick: Option<f64>,
    pub volume_multiple: Option<i32>,
}

#[derive(Debug, Default)]
pub struct CtpQueryRuntime {
    pending_instrument_requests: HashSet<String>,
    completed_instrument_requests: HashSet<String>,
    instrument_records: HashMap<String, Vec<CtpInstrumentRecord>>,
}

impl CtpQueryRuntime {
    pub fn on_command(&mut self, command: &CtpCommand) {
        if command.kind != CtpCommandKind::QueryInstruments {
            return;
        }
        if let Some(request_id) = &command.request_id {
            self.pending_instrument_requests.insert(request_id.clone());
            self.completed_instrument_requests.remove(request_id);
            self.instrument_records.entry(request_id.clone()).or_default();
        }
    }

    pub fn on_event(&mut self, event: &CtpEvent) {
        let Some(request_id) = &event.request_id else {
            return;
        };

        match event.kind {
            CtpEventKind::Instrument => {
                let venue_symbol = event
                    .venue_symbol
                    .clone()
                    .or_else(|| event.payload.get("venue_symbol").cloned())
                    .unwrap_or_default();
                self.instrument_records
                    .entry(request_id.clone())
                    .or_default()
                    .push(CtpInstrumentRecord {
                        venue_symbol,
                        exchange_id: event
                            .exchange_id
                            .clone()
                            .or_else(|| event.payload.get("exchange_id").cloned()),
                        product_class: event.payload.get("product_class").cloned(),
                        instrument_name: event.payload.get("instrument_name").cloned(),
                        price_tick: event
                            .payload
                            .get("price_tick")
                            .and_then(|value| value.parse::<f64>().ok()),
                        volume_multiple: event
                            .payload
                            .get("volume_multiple")
                            .and_then(|value| value.parse::<i32>().ok()),
                    });
            }
            CtpEventKind::InstrumentEnd => {
                self.pending_instrument_requests.remove(request_id);
                self.completed_instrument_requests.insert(request_id.clone());
            }
            _ => {}
        }
    }

    pub fn pending_instrument_query_count(&self) -> usize {
        self.pending_instrument_requests.len()
    }
}
