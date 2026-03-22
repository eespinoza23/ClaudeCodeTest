$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add('http://localhost:8080/')
$listener.Start()
Write-Host "Server running at http://localhost:8080/"
Write-Host "Press Ctrl+C to stop."

$root = $PSScriptRoot

while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response

    $path = $request.Url.LocalPath
    if ($path -eq '/') { $path = '/index.html' }

    # Build simple index if index.html doesn't exist
    if ($path -eq '/index.html' -and -not (Test-Path "$root\index.html")) {
        $body = @"
<!DOCTYPE html><html><head><title>Games</title>
<style>body{font-family:sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;margin:0;background:#111;color:#eee;}
a{color:#4af;font-size:1.5rem;margin:1rem;text-decoration:none;}a:hover{text-decoration:underline;}</style>
</head><body><h1>Games</h1>
<a href="/shooter.html">SURVIVOR (Shooter)</a>
<a href="/tictactoe.html">Tic Tac Toe</a>
</body></html>
"@
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
        $response.ContentType = 'text/html; charset=utf-8'
        $response.ContentLength64 = $bytes.Length
        $response.OutputStream.Write($bytes, 0, $bytes.Length)
        $response.Close()
        continue
    }

    $filePath = Join-Path $root ($path.TrimStart('/').Replace('/', '\'))

    if (Test-Path $filePath -PathType Leaf) {
        $ext = [System.IO.Path]::GetExtension($filePath)
        $mime = switch ($ext) {
            '.html' { 'text/html; charset=utf-8' }
            '.js'   { 'application/javascript' }
            '.css'  { 'text/css' }
            '.png'  { 'image/png' }
            '.jpg'  { 'image/jpeg' }
            default { 'application/octet-stream' }
        }
        $bytes = [System.IO.File]::ReadAllBytes($filePath)
        $response.ContentType = $mime
        $response.ContentLength64 = $bytes.Length
        $response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
        $response.StatusCode = 404
        $msg = [System.Text.Encoding]::UTF8.GetBytes('404 Not Found')
        $response.ContentLength64 = $msg.Length
        $response.OutputStream.Write($msg, 0, $msg.Length)
    }
    $response.Close()
}
