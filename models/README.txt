Place model files here:

1. inswapper_128.onnx  (~530 MB)  REQUIRED
   Download (Windows PowerShell):
     Invoke-WebRequest -Uri "https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx" -OutFile "inswapper_128.onnx"

   Download (Linux/Mac):
     wget -O inswapper_128.onnx https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx

2. buffalo_l  (~300 MB)  AUTO-DOWNLOADS on first run
   InsightFace downloads this automatically to %USERPROFILE%\.insightface\models\

Do NOT commit .onnx or .pth files to GitHub — they are in .gitignore.
