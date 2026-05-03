$ErrorActionPreference = 'Stop'

$repoRoot = 'D:\Nautilus\nautilus_ctp_adapter'
$outputDir = Join-Path $repoRoot 'output\reports\proxy_reboot_validation'
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$jsonPath = Join-Path $outputDir ("report_{0}.json" -f $timestamp)
$mdPath = Join-Path $outputDir ("report_{0}.md" -f $timestamp)
$latestJsonPath = Join-Path $outputDir 'latest.json'
$latestMdPath = Join-Path $outputDir 'latest.md'
$taskName = '3proxy-post-reboot-validate'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Invoke-WithRetry {
    param(
        [scriptblock]$Script,
        [int]$Attempts = 10,
        [int]$DelaySeconds = 15
    )

    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        try {
            return & $Script
        }
        catch {
            if ($attempt -eq $Attempts) {
                throw
            }
            Start-Sleep -Seconds $DelaySeconds
        }
    }
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Script
    )

    try {
        [ordered]@{
            ok = $true
            data = & $Script
        }
    }
    catch {
        [ordered]@{
            ok = $false
            error = $_.Exception.Message
        }
    }
}

$report = [ordered]@{
    timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    hostname = $env:COMPUTERNAME
    repo_root = $repoRoot
}

$report.service = Invoke-Step 'service' {
    Invoke-WithRetry {
        $service = Get-Service 3proxy-egress -ErrorAction Stop
        if ($service.Status -ne 'Running') {
            throw '3proxy-egress is not running yet.'
        }

        [ordered]@{
            name = $service.Name
            status = $service.Status.ToString()
            start_type = $service.StartType.ToString()
            qc = (sc.exe qc 3proxy-egress | Out-String).Trim()
            qfailure = (sc.exe qfailure 3proxy-egress | Out-String).Trim()
        }
    }
}

$report.listener = Invoke-Step 'listener' {
    Invoke-WithRetry {
        $listeners = Get-NetTCPConnection -State Listen -LocalAddress '10.168.80.56' -ErrorAction Stop |
            Where-Object { $_.LocalPort -in 3128, 1080 } |
            Select-Object LocalAddress, LocalPort, OwningProcess

        $ports = $listeners | Select-Object -ExpandProperty LocalPort -Unique | Sort-Object
        if (($ports -join ',') -ne '1080,3128') {
            throw 'Expected listeners on 10.168.80.56:1080 and 10.168.80.56:3128.'
        }

        $listeners
    }
}

$report.nic = Invoke-Step 'nic' {
    $ingress = Get-NetIPAddress -IPAddress '10.168.80.56' -ErrorAction Stop |
        Select-Object -First 1 InterfaceAlias, InterfaceIndex, IPAddress
    $egress = Get-NetIPAddress -IPAddress '192.168.5.235' -ErrorAction Stop |
        Select-Object -First 1 InterfaceAlias, InterfaceIndex, IPAddress
    $indices = @($ingress.InterfaceIndex, $egress.InterfaceIndex) | Sort-Object -Unique

    [ordered]@{
        ingress = $ingress
        egress = $egress
        interfaces = Get-NetIPInterface |
            Where-Object { $_.InterfaceIndex -in $indices } |
            Select-Object InterfaceAlias, InterfaceIndex, AddressFamily, InterfaceMetric, Dhcp, ConnectionState
        dns = Get-DnsClientServerAddress |
            Where-Object { $_.InterfaceIndex -in $indices } |
            Select-Object InterfaceAlias, InterfaceIndex, AddressFamily, ServerAddresses
    }
}

$report.local_proxy = Invoke-Step 'local_proxy' {
    Invoke-WithRetry {
        $github = Invoke-WebRequest -Proxy http://10.168.80.56:3128 https://github.com -UseBasicParsing -TimeoutSec 30
        $ipify = Invoke-WebRequest -Proxy http://10.168.80.56:3128 https://api.ipify.org -UseBasicParsing -TimeoutSec 30

        [ordered]@{
            github_status = [int]$github.StatusCode
            egress_ip = $ipify.Content.Trim()
        }
    }
}

$report.local_default = Invoke-Step 'local_default' {
    Invoke-WithRetry {
        $youtube = Invoke-WebRequest https://www.youtube.com -UseBasicParsing -TimeoutSec 30
        $google = Invoke-WebRequest https://www.google.com -UseBasicParsing -TimeoutSec 30

        [ordered]@{
            youtube_status = [int]$youtube.StatusCode
            google_status = [int]$google.StatusCode
        }
    }
}

$report.remote = Invoke-Step 'remote' {
    Invoke-WithRetry {
        $secure = ConvertTo-SecureString 'Love0417!@' -AsPlainText -Force
        $credential = New-Object System.Management.Automation.PSCredential('DESK-8058\kimi', $secure)

        Invoke-Command -ComputerName 10.168.80.58 -Credential $credential -ErrorAction Stop -ScriptBlock {
            $port = Test-NetConnection 10.168.80.56 -Port 3128 -WarningAction SilentlyContinue
            $response = Invoke-WebRequest -Proxy http://10.168.80.56:3128 https://github.com -UseBasicParsing -TimeoutSec 30
            $git = git -c http.proxy=http://10.168.80.56:3128 -c https.proxy=http://10.168.80.56:3128 ls-remote https://github.com/github/gitignore.git HEAD 2>$null

            [ordered]@{
                proxy_port_ok = [bool]$port.TcpTestSucceeded
                github_status = [int]$response.StatusCode
                github_git_ok = [bool]$git
                head = if ($git) { ($git | Select-Object -First 1) } else { '' }
            }
        }
    }
}

$report.overall_ok = (
    $report.service.ok -and
    $report.listener.ok -and
    $report.nic.ok -and
    $report.local_proxy.ok -and
    $report.local_default.ok -and
    $report.remote.ok -and
    $report.local_proxy.data.github_status -eq 200 -and
    $report.local_default.data.youtube_status -eq 200 -and
    $report.local_default.data.google_status -eq 200 -and
    $report.remote.data.proxy_port_ok -and
    $report.remote.data.github_status -eq 200 -and
    $report.remote.data.github_git_ok
)

$json = $report | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($jsonPath, $json, $utf8NoBom)
[System.IO.File]::WriteAllText($latestJsonPath, $json, $utf8NoBom)

$markdown = @(
    '# Proxy Reboot Validation',
    '',
    "- timestamp: $($report.timestamp)",
    "- hostname: $($report.hostname)",
    "- overall_ok: $($report.overall_ok)",
    '',
    '## Service',
    "- ok: $($report.service.ok)",
    "- status: $($report.service.data.status)",
    '',
    '## Listener',
    "- ok: $($report.listener.ok)",
    '',
    '## Local Proxy',
    "- ok: $($report.local_proxy.ok)",
    "- github_status: $($report.local_proxy.data.github_status)",
    "- egress_ip: $($report.local_proxy.data.egress_ip)",
    '',
    '## Local Default',
    "- ok: $($report.local_default.ok)",
    "- youtube_status: $($report.local_default.data.youtube_status)",
    "- google_status: $($report.local_default.data.google_status)",
    '',
    '## Remote 10.168.80.58',
    "- ok: $($report.remote.ok)",
    "- proxy_port_ok: $($report.remote.data.proxy_port_ok)",
    "- github_status: $($report.remote.data.github_status)",
    "- github_git_ok: $($report.remote.data.github_git_ok)",
    "- head: $($report.remote.data.head)",
    ''
) -join "`r`n"

[System.IO.File]::WriteAllText($mdPath, $markdown, $utf8NoBom)
[System.IO.File]::WriteAllText($latestMdPath, $markdown, $utf8NoBom)

try {
    schtasks.exe /Delete /TN $taskName /F | Out-Null
}
catch {
}