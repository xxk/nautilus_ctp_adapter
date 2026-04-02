use std::collections::VecDeque;

use crate::commands::CtpCommand;
use crate::config::CtpRuntimeConfig;
use crate::events::CtpEvent;
use crate::market::CtpMarketRuntime;
use crate::session::CtpSessionRuntime;
use crate::trading::CtpTradingRuntime;

#[derive(Debug, Clone, Default)]
pub struct NativeRuntime {
    connected: bool,
    config: Option<CtpRuntimeConfig>,
    session: CtpSessionRuntime,
    market: CtpMarketRuntime,
    trading: CtpTradingRuntime,
    commands: VecDeque<CtpCommand>,
    events: VecDeque<CtpEvent>,
}

impl NativeRuntime {
    /// This runtime is the host-neutral side of the repository-owned `ctp_native`
    /// boundary. It should consume normalized commands/events and avoid taking a
    /// dependency on Nautilus or any temporary bootstrap host.
    pub fn new() -> Self {
        Self::default()
    }

    pub fn configure(&mut self, config: CtpRuntimeConfig) {
        self.config = Some(config);
    }

    pub fn is_connected(&self) -> bool {
        self.connected
    }

    pub fn session(&self) -> &CtpSessionRuntime {
        &self.session
    }

    pub fn market(&self) -> &CtpMarketRuntime {
        &self.market
    }

    pub fn trading(&self) -> &CtpTradingRuntime {
        &self.trading
    }

    pub fn submit_command(&mut self, command: CtpCommand) {
        self.session.on_command(&command);
        self.market.on_command(&command);
        self.trading.on_command(&command);
        self.commands.push_back(command);
    }

    pub fn drain_submitted_commands(&mut self, limit: Option<usize>) -> Vec<CtpCommand> {
        let remaining = limit.unwrap_or(self.commands.len()).min(self.commands.len());
        let mut drained = Vec::with_capacity(remaining);
        for _ in 0..remaining {
            if let Some(command) = self.commands.pop_front() {
                drained.push(command);
            }
        }
        drained
    }

    pub fn push_event(&mut self, event: CtpEvent) {
        self.session.on_event(&event);
        self.trading.on_event(&event);
        self.connected = self.session.is_connected();
        self.events.push_back(event);
    }

    pub fn drain_events(&mut self, limit: Option<usize>) -> Vec<CtpEvent> {
        let remaining = limit.unwrap_or(self.events.len()).min(self.events.len());
        let mut drained = Vec::with_capacity(remaining);
        for _ in 0..remaining {
            if let Some(event) = self.events.pop_front() {
                drained.push(event);
            }
        }
        drained
    }

    pub fn pending_command_count(&self) -> usize {
        self.commands.len()
    }

    pub fn pending_event_count(&self) -> usize {
        self.events.len()
    }
}
