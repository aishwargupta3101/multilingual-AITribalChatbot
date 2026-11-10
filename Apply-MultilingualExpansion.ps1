$ErrorActionPreference = 'Stop'
$root = (Get-Location).Path
$servicePath = Join-Path $root 'backend/translation/indictrans_service.py'
$translationPath = Join-Path $root 'backend/translation/translation_service.py'
$constantsPath = Join-Path $root 'frontend/utils/constants.py'
$sidebarPath = Join-Path $root 'frontend/components/sidebar.py'
foreach ($p in @($servicePath,$translationPath,$constantsPath,$sidebarPath)) { if (-not (Test-Path $p)) { throw "Run this script from the project root. Missing: $p" } }

# IndicTrans2 codes. Apply additively so current local improvements are preserved.
$s = Get-Content $servicePath -Raw
$codeAnchor = '"manipuri_mayek": "mni_Mtei",'
$codeBlock = @'
"manipuri_mayek": "mni_Mtei",
        "assamese": "asm_Beng", "bengali": "ben_Beng", "bodo": "brx_Deva",
        "dogri": "doi_Deva", "gujarati": "guj_Gujr", "kannada": "kan_Knda",
        "kashmiri": "kas_Arab", "kashmiri_deva": "kas_Deva", "konkani": "gom_Deva",
        "maithili": "mai_Deva", "malayalam": "mal_Mlym", "marathi": "mar_Deva",
        "nepali": "npi_Deva", "odia": "ory_Orya", "punjabi": "pan_Guru",
        "sanskrit": "san_Deva", "sindhi": "snd_Arab", "sindhi_deva": "snd_Deva",
        "tamil": "tam_Taml", "telugu": "tel_Telu", "urdu": "urd_Arab", "santali": "sat_Olck",
'@
if (-not $s.Contains('"assamese": "asm_Beng"')) {
    if (-not $s.Contains($codeAnchor)) { throw 'Could not find the IndicTrans language-code insertion point. No service changes applied.' }
    $s = $s.Replace($codeAnchor, $codeBlock.TrimEnd())
}
$aliasAnchor = '"mni_mtei": "manipuri_mtei",'
$aliasBlock = @'
"mni_mtei": "manipuri_mtei",
        "as": "assamese", "asm": "assamese", "bn": "bengali", "ben": "bengali",
        "brx": "bodo", "doi": "dogri", "gu": "gujarati", "kn": "kannada",
        "ks": "kashmiri", "kas_deva": "kashmiri_deva", "gom": "konkani", "mai": "maithili",
        "ml": "malayalam", "mr": "marathi", "ne": "nepali", "or": "odia", "pa": "punjabi",
        "sa": "sanskrit", "sd": "sindhi", "snd_deva": "sindhi_deva", "ta": "tamil",
        "te": "telugu", "ur": "urdu", "sat": "santali", "sat_olck": "santali",
'@
if (-not $s.Contains('"sat_olck": "santali"')) {
    if ($s.Contains($aliasAnchor)) { $s = $s.Replace($aliasAnchor, $aliasBlock.TrimEnd()) }
}
# Required script restoration after generation.
$s = [regex]::Replace($s, 'postprocess_batch\(decoded\s*\)', 'postprocess_batch(decoded, lang=target_code)')
# The expanded routes are explicitly beta: allow configured candidates but log them, rather than falsely calling them verified.
if ($s.Contains('VERIFIED_LANGUAGES') -and $s.Contains('not in cls.VERIFIED_LANGUAGES')) {
    $pattern = '(?s)if language not in cls\.VERIFIED_LANGUAGES:\s*raise ValueError\(\s*f"IndicTrans2 support has not yet been verified for: \{language\}\. "\s*"Verify the installed model checkpoint before enabling this route\."\s*\)'
        
$replacement = @'
if language not in cls.VERIFIED_LANGUAGES:
            logger.warning("Using experimental IndicTrans2 language mapping: %s", language)
'@

$s = [regex]::Replace($s, $pattern, $replacement)
}
Set-Content $servicePath $s -Encoding UTF8

# Expose the scheduled languages through the central text-translation service.
$t = Get-Content $translationPath -Raw
if ($t -notmatch '"assamese"') {
    $t = [regex]::Replace($t, '(?s)(SUPPORTED_LANGUAGES\s*=\s*\{)(.*?)(\})', {
        param($m) $m.Groups[1].Value + $m.Groups[2].Value + "`n        " + '"assamese", "bengali", "bodo", "dogri", "gujarati", "kannada", "kashmiri", "kashmiri_deva", "konkani", "maithili", "malayalam", "marathi", "nepali", "odia", "punjabi", "sanskrit", "sindhi", "sindhi_deva", "tamil", "telugu", "urdu", "santali",' + $m.Groups[3].Value
    }, 1)
}
if ($t.Contains('elif source_language == "manipuri" or target_language in {"manipuri", "hindi"}:')) {
    $t = $t.Replace('elif source_language == "manipuri" or target_language in {"manipuri", "hindi"}:', 'elif source_language == "manipuri" or target_language == "manipuri":')
}
Set-Content $translationPath $t -Encoding UTF8

# Main chat language selector. Preserve the existing tribal/regional modes.
$c = Get-Content $constantsPath -Raw
$languageList = @'
SUPPORTED_LANGUAGES = [
    "english", "hindi", "assamese", "bengali", "bodo", "dogri", "gujarati",
    "kannada", "kashmiri", "kashmiri_deva", "konkani", "maithili", "malayalam",
    "manipuri", "manipuri_mtei", "marathi", "nepali", "odia", "punjabi", "sanskrit",
    "santali", "sindhi", "sindhi_deva", "tamil", "telugu", "urdu",
    "tai_khamti", "monpa", "naga", "mishmi"
]
'@
$c = [regex]::Replace($c, '(?s)SUPPORTED_LANGUAGES\s*=\s*\[.*?\]', $languageList.Trim(), 1)
Set-Content $constantsPath $c -Encoding UTF8

# Human-readable labels for the selector.
$b = Get-Content $sidebarPath -Raw
$display = @'
LANGUAGE_DISPLAY_NAMES = {
            "english": "English", "hindi": "Hindi", "assamese": "Assamese",
            "bengali": "Bengali", "bodo": "Bodo", "dogri": "Dogri", "gujarati": "Gujarati",
            "kannada": "Kannada", "kashmiri": "Kashmiri (Arabic script)",
            "kashmiri_deva": "Kashmiri (Devanagari; beta)", "konkani": "Konkani",
            "maithili": "Maithili", "malayalam": "Malayalam",
            "manipuri": "Manipuri (Bengali Script)", "manipuri_mtei": "Manipuri (Meitei Mayek)",
            "marathi": "Marathi", "nepali": "Nepali", "odia": "Odia", "punjabi": "Punjabi",
            "sanskrit": "Sanskrit", "santali": "Santali (Ol Chiki)",
            "sindhi": "Sindhi (Arabic script)", "sindhi_deva": "Sindhi (Devanagari; beta)",
            "tamil": "Tamil", "telugu": "Telugu", "urdu": "Urdu",
            "monpa": "Monpa (experimental)", "tai_khamti": "Tai Khamti (RAG)",
            "naga": "Naga (experimental)", "mishmi": "Mishmi (experimental)"
        }
'@
$b = [regex]::Replace($b, '(?s)LANGUAGE_DISPLAY_NAMES\s*=\s*\{.*?\}', $display.Trim(), 1)
Set-Content $sidebarPath $b -Encoding UTF8

# Syntax-check changed Python files once at the end.
python -m py_compile $servicePath $translationPath $constantsPath $sidebarPath
if ($LASTEXITCODE -ne 0) { throw 'Python syntax check failed. Review the error above.' }
Write-Host 'Multilingual text-translation patch applied and Python syntax checks passed.' -ForegroundColor Green
Write-Host 'New languages are enabled as experimental text translation; audio/STT/TTS support is not implied.'
