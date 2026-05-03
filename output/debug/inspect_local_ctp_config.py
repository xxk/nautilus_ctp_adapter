import json
from pathlib import Path
paths = [Path('cfgs/local/ctp.live.025292.local.json'), Path('cfgs/local/ctp.live.025292.rb2610.10675.json')]
for path in paths:
    if not path.exists():
        print(json.dumps({'path': str(path), 'exists': False}, ensure_ascii=False))
        continue
    payload = json.loads(path.read_text(encoding='utf-8'))
    safe = {
        'path': str(path),
        'exists': True,
        'BrokerID': payload.get('BrokerID') or payload.get('broker_id') or payload.get('经纪商代码'),
        'UserID': payload.get('UserID') or payload.get('user_id') or payload.get('用户名'),
        'Host': payload.get('Host') or payload.get('td_front') or payload.get('交易服务器'),
        'Pricer': payload.get('Pricer') or payload.get('md_front') or payload.get('行情服务器'),
        'AppID': payload.get('AppID') or payload.get('app_id'),
        'ProductInfo': payload.get('ProductInfo') or payload.get('product_info') or payload.get('产品名称') or payload.get('Service') or payload.get('service'),
        'PasswordPresent': bool(payload.get('Password') or payload.get('password') or payload.get('密码')),
        'AuthCodePresent': bool(payload.get('AuthCode') or payload.get('auth_code') or payload.get('授权编码')),
        'NativePackDir': payload.get('NativePackDir') or payload.get('native_pack_dir'),
        'ManagedAssemblyDir': payload.get('ManagedAssemblyDir') or payload.get('managed_assembly_dir'),
    }
    print(json.dumps(safe, ensure_ascii=False))
