void OnFrontConnected(){ ReqUserLogin(&m_logonField, 0); }
void OnRspUserLogin(){ SubscribeMarketData(c_inst, 1); }
