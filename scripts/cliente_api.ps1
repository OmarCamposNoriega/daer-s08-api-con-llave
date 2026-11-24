param(
    [string]$BaseUrl = 'http://127.0.0.1:8000',
    [string]$Token = 'admin-token-de-laboratorio-0000000000001'
)

$ErrorActionPreference = 'Stop'

$headers = @{
    'Authorization' = "Token $Token"
    'Content-Type'  = 'application/json; charset=utf-8'
}

function Invoke-ApiStep {
    param(
        [string]$Label,
        [string]$Method,
        [string]$Uri,
        [hashtable]$Body = $null
    )

    $params = @{
        Method          = $Method
        Uri             = $Uri
        Headers         = $headers
        UseBasicParsing = $true
    }
    if ($null -ne $Body) {
        $json = $Body | ConvertTo-Json -Compress
        $params['Body'] = [System.Text.Encoding]::UTF8.GetBytes($json)
    }

    try {
        $resp = Invoke-WebRequest @params
        $code = [int]$resp.StatusCode
        $content = $resp.Content
        Write-Host "[$Label] $Method $Uri -> HTTP $code"
        if ($content) {
            Write-Host "  Respuesta: $content"
        }
        if ($content) {
            return ($content | ConvertFrom-Json)
        }
        return $null
    } catch {
        $webResp = $_.Exception.Response
        if ($null -ne $webResp) {
            $code = [int]$webResp.StatusCode
            $reader = New-Object System.IO.StreamReader($webResp.GetResponseStream())
            $errBody = $reader.ReadToEnd()
            Write-Host "[$Label] $Method $Uri -> HTTP $code"
            if ($errBody) {
                Write-Host "  Respuesta: $errBody"
            }
            return $null
        }
        throw
    }
}

Write-Host "=== Cliente API PowerShell (ciclo CRUD con token admin) ==="

# 1. Crear producto (POST -> 201 Created)
$creado = Invoke-ApiStep -Label '1. CREAR' -Method 'POST' -Uri "$BaseUrl/api/productos/" -Body @{
    nombre      = 'Inca Kola 500ml'
    categoria   = 3
    precio      = '2.50'
    stock       = 15
    descripcion = 'Gaseosa peruana sabor tradicional.'
}

$prodId = $creado.id

# 2. Modificar producto (PATCH -> 200 OK)
$null = Invoke-ApiStep -Label '2. MODIFICAR' -Method 'PATCH' -Uri "$BaseUrl/api/productos/$prodId/" -Body @{
    precio = '2.80'
    stock  = 20
}

# 3. Consultar producto (GET -> 200 OK)
$null = Invoke-ApiStep -Label '3. CONSULTAR' -Method 'GET' -Uri "$BaseUrl/api/productos/$prodId/"

# 4. Borrar producto (DELETE -> 204 No Content)
$null = Invoke-ApiStep -Label '4. BORRAR' -Method 'DELETE' -Uri "$BaseUrl/api/productos/$prodId/"

# 5. Consultar tras borrado (GET -> 404 Not Found)
$null = Invoke-ApiStep -Label '5. VERIFICAR BORRADO' -Method 'GET' -Uri "$BaseUrl/api/productos/$prodId/"
