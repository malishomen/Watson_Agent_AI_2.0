[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "UTF-8"
$env:UVICORN_ACCESS_LOG = "0"
$env:UVICORN_LOG_LEVEL = "info"
if (-not $env:WATSON_API_BASE) { $env:WATSON_API_BASE = "http://127.0.0.1:8090" }
if (-not $env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL = "http://127.0.0.1:1234/v1" }
if (-not $env:OPENAI_API_KEY)  { $env:OPENAI_API_KEY  = "lm-studio" }
if (-not $env:WATSON_PLANNER_MODEL) { $env:WATSON_PLANNER_MODEL = "deepseek-r1-distill-qwen-14b-abliterated-v2" }
if (-not $env:WATSON_CODER_MODEL)   { $env:WATSON_CODER_MODEL   = "qwen2.5-coder-7b-instruct" }
$PSStyle.OutputRendering = "Ansi"
Write-Output "🟢 UTF-8 environment prepared."


