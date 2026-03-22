$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$wb = $excel.Workbooks.Open('C:\Users\learn\Desktop\SAFe PI Schedule_V5 - WIP.xlsx')
foreach ($sheet in $wb.Sheets) {
    Write-Host "=== Sheet: $($sheet.Name) ==="
    $used = $sheet.UsedRange
    $rows = [Math]::Min($used.Rows.Count, 100)
    $cols = $used.Columns.Count
    Write-Host "Size: $($used.Rows.Count) rows x $cols cols"
    for ($r = 1; $r -le $rows; $r++) {
        $line = ""
        for ($c = 1; $c -le $cols; $c++) {
            $val = $sheet.Cells($r, $c).Text
            if ($val -ne "") { $line += "[$c=$val] " }
        }
        if ($line -ne "") { Write-Host "R${r}: $line" }
    }
}
$wb.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "DONE"
