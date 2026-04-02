use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct CtpRuntimeConfig {
    pub broker_id: String,
    pub user_id: String,
    pub auth_code: String,
    pub app_id: String,
    pub md_front: String,
    pub td_front: String,
    pub product_info: String,
    pub client_id: i32,
    pub provider_id: u8,
}
