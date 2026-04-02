use std::collections::BTreeMap;

use crate::commands::{CtpCommand, CtpCommandKind};
use crate::events::{CtpEvent, CtpEventKind};

#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub enum CtpOrderState {
    #[default]
    Unknown,
    PendingSubmit,
    Working,
    PendingCancel,
    PendingReplace,
    Filled,
    Cancelled,
}

#[derive(Debug, Clone, Default)]
pub struct CtpTradingRuntime {
    order_states: BTreeMap<String, CtpOrderState>,
}

impl CtpTradingRuntime {
    pub fn on_command(&mut self, command: &CtpCommand) {
        let Some(client_order_id) = command.client_order_id.as_ref() else {
            return;
        };

        match command.kind {
            CtpCommandKind::SubmitOrder => {
                self.order_states
                    .insert(client_order_id.clone(), CtpOrderState::PendingSubmit);
            }
            CtpCommandKind::CancelOrder => {
                self.order_states
                    .insert(client_order_id.clone(), CtpOrderState::PendingCancel);
            }
            CtpCommandKind::ReplaceOrder => {
                self.order_states
                    .insert(client_order_id.clone(), CtpOrderState::PendingReplace);
            }
            _ => {}
        }
    }

    pub fn on_event(&mut self, event: &CtpEvent) {
        let Some(client_order_id) = event.client_order_id.as_ref() else {
            return;
        };

        match event.kind {
            CtpEventKind::Order => {
                self.order_states
                    .insert(client_order_id.clone(), CtpOrderState::Working);
            }
            CtpEventKind::Trade => {
                self.order_states
                    .insert(client_order_id.clone(), CtpOrderState::Filled);
            }
            CtpEventKind::Error => {
                self.order_states
                    .entry(client_order_id.clone())
                    .or_insert(CtpOrderState::Unknown);
            }
            _ => {}
        }
    }

    pub fn state_for(&self, client_order_id: &str) -> CtpOrderState {
        self.order_states
            .get(client_order_id)
            .copied()
            .unwrap_or(CtpOrderState::Unknown)
    }

    pub fn tracked_order_count(&self) -> usize {
        self.order_states.len()
    }
}
