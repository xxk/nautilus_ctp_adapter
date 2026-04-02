use crate::commands::{CtpCommand, CtpCommandKind};
use crate::events::{CtpEvent, CtpEventKind};

#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub enum CtpSessionState {
    #[default]
    Disconnected,
    Connecting,
    Connected,
    Authenticated,
    LoggedIn,
}

#[derive(Debug, Clone, Default)]
pub struct CtpSessionRuntime {
    state: CtpSessionState,
}

impl CtpSessionRuntime {
    pub fn on_command(&mut self, command: &CtpCommand) {
        match command.kind {
            CtpCommandKind::Connect => self.state = CtpSessionState::Connecting,
            CtpCommandKind::Disconnect => self.state = CtpSessionState::Disconnected,
            _ => {}
        }
    }

    pub fn on_event(&mut self, event: &CtpEvent) {
        match event.kind {
            CtpEventKind::Connected => self.state = CtpSessionState::Connected,
            CtpEventKind::AuthSucceeded => self.state = CtpSessionState::Authenticated,
            CtpEventKind::LoginSucceeded => self.state = CtpSessionState::LoggedIn,
            CtpEventKind::Disconnected | CtpEventKind::AuthFailed | CtpEventKind::LoginFailed => {
                self.state = CtpSessionState::Disconnected
            }
            _ => {}
        }
    }

    pub fn state(&self) -> CtpSessionState {
        self.state
    }

    pub fn is_connected(&self) -> bool {
        matches!(
            self.state,
            CtpSessionState::Connected | CtpSessionState::Authenticated | CtpSessionState::LoggedIn
        )
    }
}
