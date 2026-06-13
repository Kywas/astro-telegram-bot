$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$marketing = Join-Path $root "marketing"
$edge = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) {
    $edge = "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe"
}
if (-not (Test-Path $edge)) {
    Write-Error "Microsoft Edge not found. Open marketing/*.html in a browser and screenshot manually."
}

$posts = @(
    @{ Html = "post-1-intro.html"; Png = "post-1-intro.png"; Size = "1080,1080" },
    @{ Html = "post-2-compat.html"; Png = "post-2-compat.png"; Size = "1080,1080" },
    @{ Html = "mts-telegram-ad.html"; Png = "mts-telegram-ad.png"; Size = "1280,720" }
)

foreach ($post in $posts) {
    $htmlPath = (Resolve-Path (Join-Path $marketing $post.Html)).Path
    $pngPath = Join-Path $marketing $post.Png
    $uri = "file:///" + ($htmlPath -replace "\\", "/")
    & $edge --headless --disable-gpu --hide-scrollbars --window-size=$($post.Size) --screenshot="$pngPath" "$uri"
    Write-Host "OK $($post.Png)"
}
