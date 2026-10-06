param(
    [int]$PauseMilliseconds = 250,
    [int]$MaxPages = 100,
    [string[]]$OnlyRepository
)

$ErrorActionPreference = 'Stop'
$headers = @{
    Accept = 'application/vnd.github+json'
    'X-GitHub-Api-Version' = '2026-03-10'
    'User-Agent' = 'AI-Tech-Trend-Radar-Data-Spike'
}

$repositories = @(
    @{ technology = 'LangGraph'; repository = 'langchain-ai/langgraph' }
    @{ technology = 'LangChain'; repository = 'langchain-ai/langchain' }
    @{ technology = 'LlamaIndex'; repository = 'run-llama/llama_index' }
    @{ technology = 'CrewAI'; repository = 'crewAIInc/crewAI' }
    @{ technology = 'PydanticAI'; repository = 'pydantic/pydantic-ai' }
    @{ technology = 'DSPy'; repository = 'stanfordnlp/dspy' }
    @{ technology = 'LiteLLM'; repository = 'BerriAI/litellm' }
    @{ technology = 'vLLM'; repository = 'vllm-project/vllm' }
    @{ technology = 'Ollama'; repository = 'ollama/ollama' }
    @{ technology = 'Dify'; repository = 'langgenius/dify' }
)

if ($OnlyRepository) {
    $repositories = @($repositories | Where-Object { $OnlyRepository -contains $_.repository })
}

$results = foreach ($item in $repositories) {
    $rows = @()
    $page = 1
    $status = 'PASS'
    $errorMessage = $null

    try {
        do {
            $url = "https://api.github.com/repos/$($item.repository)/stargazers/history?per_page=30&page=$page"
            $response = Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing
            # Windows PowerShell 5.1 may collapse a top-level JSON array into one
            # object whose properties are arrays. Normalize both response shapes.
            $parsed = ConvertFrom-Json -InputObject $response.Content
            if ($parsed.week -is [System.Array]) {
                $pageRows = for ($i = 0; $i -lt $parsed.week.Count; $i++) {
                    [pscustomobject]@{
                        week = $parsed.week[$i]
                        total = $parsed.total[$i]
                        days = @($parsed.days | Select-Object -Skip ($i * 7) -First 7)
                    }
                }
            }
            else {
                $pageRows = @($parsed)
            }
            $rows += $pageRows
            $page++

            if ($PauseMilliseconds -gt 0) {
                Start-Sleep -Milliseconds $PauseMilliseconds
            }
        } while ($pageRows.Count -eq 30 -and $page -le $MaxPages)
    }
    catch {
        $status = 'PENDING'
        $errorMessage = $_.Exception.Message
    }

    $uniqueRows = @($rows | Where-Object { $null -ne $_.week } | Sort-Object week -Unique)
    $first = $uniqueRows | Select-Object -First 1
    $last = $uniqueRows | Select-Object -Last 1
    $hasValidDays = $uniqueRows.Count -gt 0 -and (@($uniqueRows | Where-Object { @($_.days).Count -ne 7 }).Count -eq 0)

    if ($status -eq 'PASS' -and $uniqueRows.Count -lt 104) {
        $status = 'FAIL'
    }

    [pscustomobject]@{
        technology = $item.technology
        repository = $item.repository
        status = $status
        weeks = $uniqueRows.Count
        pages = $page - 1
        has_104_weeks = $uniqueRows.Count -ge 104
        days_length_valid = $hasValidDays
        newest_week = if ($last) { $last.week } else { $null }
        oldest_week = if ($first) { $first.week } else { $null }
        sample_total = if ($last) { $last.total } else { $null }
        error = $errorMessage
    }
}

$results | ConvertTo-Json -Depth 5
