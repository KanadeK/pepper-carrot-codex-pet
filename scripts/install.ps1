param(
    [string]$Ref = $env:PEPPER_CARROT_REF,
    [string]$SourceRoot = ""
)

$ErrorActionPreference = "Stop"
$Repository = if ([string]::IsNullOrWhiteSpace($env:PEPPER_CARROT_REPOSITORY)) {
    "KanadeK/pepper-carrot-codex-pet"
} else {
    $env:PEPPER_CARROT_REPOSITORY
}
$PetId = "pepper-carrot"
$Payload = @("pet.json", "spritesheet.webp", "provenance.json")

if ([string]::IsNullOrWhiteSpace($Ref)) {
    $Ref = "main"
}

$codexRoot = if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
    Join-Path $env:USERPROFILE ".codex"
} else {
    $env:CODEX_HOME
}

$petsRoot = Join-Path $codexRoot "pets"
$target = Join-Path $petsRoot $PetId
$backupRoot = Join-Path $codexRoot "pet-backups"
$stageRoot = $null
$backupPath = $null
$installed = $false

function Assert-Checksum {
    param(
        [string]$FilePath,
        [string]$RelativePath,
        [string[]]$ChecksumLines
    )

    $escaped = [regex]::Escape($RelativePath)
    $line = $ChecksumLines |
        Where-Object { $_ -match "^[a-fA-F0-9]{64}\s+$escaped$" } |
        Select-Object -First 1
    if ($null -eq $line) {
        throw "Missing checksum for $RelativePath"
    }

    $expected = ($line -split "\s+")[0].ToLowerInvariant()
    $actual = (Get-FileHash -LiteralPath $FilePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) {
        throw "Checksum mismatch for $RelativePath"
    }
}

try {
    if (Test-Path -LiteralPath $petsRoot) {
        $petsRootItem = Get-Item -LiteralPath $petsRoot -Force
        if (($petsRootItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Refusing to operate through a reparse-point pets directory"
        }
    }
    New-Item -ItemType Directory -Force -Path $petsRoot | Out-Null
    if (Test-Path -LiteralPath $target) {
        $targetItem = Get-Item -LiteralPath $target -Force
        if (($targetItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Refusing to replace a reparse-point pet directory"
        }
    }

    $stageRoot = Join-Path $petsRoot (".pepper-carrot.stage-" + [guid]::NewGuid().ToString("N"))
    $stagePet = Join-Path $stageRoot "pet"
    New-Item -ItemType Directory -Force -Path $stagePet | Out-Null
    $stageChecksums = Join-Path $stageRoot "checksums.txt"

    if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
        $rawRoot = "https://raw.githubusercontent.com/$Repository/$Ref"
        Invoke-WebRequest -UseBasicParsing "$rawRoot/checksums.txt" -OutFile $stageChecksums
        foreach ($name in $Payload) {
            Invoke-WebRequest -UseBasicParsing "$rawRoot/pet/$name" `
                -OutFile (Join-Path $stagePet $name)
        }
    } else {
        $resolvedSource = (Resolve-Path -LiteralPath $SourceRoot).Path
        Copy-Item -LiteralPath (Join-Path $resolvedSource "checksums.txt") `
            -Destination $stageChecksums
        foreach ($name in $Payload) {
            Copy-Item -LiteralPath (Join-Path $resolvedSource "pet/$name") `
                -Destination (Join-Path $stagePet $name)
        }
    }

    $checksumLines = Get-Content -LiteralPath $stageChecksums
    foreach ($name in $Payload) {
        Assert-Checksum -FilePath (Join-Path $stagePet $name) `
            -RelativePath "pet/$name" -ChecksumLines $checksumLines
    }

    $manifest = Get-Content -LiteralPath (Join-Path $stagePet "pet.json") -Raw |
        ConvertFrom-Json
    if ($manifest.id -ne $PetId -or $manifest.spriteVersionNumber -ne 2) {
        throw "Downloaded pet.json is not the Pepper Codex v2 manifest"
    }

    if (Test-Path -LiteralPath $target) {
        New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
        $timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
        $token = [guid]::NewGuid().ToString("N").Substring(0, 8)
        $backupPath = Join-Path $backupRoot "$PetId-install-$timestamp-$token"
        Move-Item -LiteralPath $target -Destination $backupPath
    }

    Move-Item -LiteralPath $stagePet -Destination $target
    $installed = $true

    Write-Host "Installed Pepper | Pepper&Carrot to $target"
    if ($null -ne $backupPath) {
        Write-Host "Previous pet backup: $backupPath"
    }
    Write-Host "Open Settings > Pets, choose Refresh, then select Pepper | Pepper&Carrot."
} catch {
    if (
        -not $installed -and
        $null -ne $backupPath -and
        -not (Test-Path -LiteralPath $target) -and
        (Test-Path -LiteralPath $backupPath)
    ) {
        Move-Item -LiteralPath $backupPath -Destination $target
    }
    throw
} finally {
    if ($null -ne $stageRoot -and (Test-Path -LiteralPath $stageRoot)) {
        Remove-Item -LiteralPath $stageRoot -Recurse -Force
    }
}
