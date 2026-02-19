#!/usr/bin/env pwsh
# Create a simple placeholder icon for testing
# Replace with professional design before production release

Write-Host "Creating placeholder app icon and splash screen..." -ForegroundColor Cyan
Write-Host ""

# Check if ImageMagick or similar is available
$hasImageMagick = Get-Command magick -ErrorAction SilentlyContinue

if ($hasImageMagick) {
    Write-Host "[OK] ImageMagick found, creating images..." -ForegroundColor Green
    
    # Create app icon (simple gradient with text)
    magick -size 1024x1024 gradient:"#4A90E2-#2E5C8A" `
        -gravity center -pointsize 200 -fill white `
        -annotate +0+0 "JS" `
        assets\icons\app_icon.png
    
    magick -size 1024x1024 gradient:"#4A90E2-#2E5C8A" `
        -gravity center -pointsize 200 -fill white `
        -annotate +0+0 "JS" `
        assets\icons\app_icon_foreground.png
    
    # Create splash logo
    magick -size 1024x1024 xc:transparent `
        -gravity center -pointsize 300 -fill "#4A90E2" `
        -annotate +0-100 "Job" `
        -pointsize 200 -fill "#2E5C8A" `
        -annotate +0+100 "Search" `
        assets\splash\splash_logo.png
    
    magick -size 1024x1024 xc:transparent `
        -gravity center -pointsize 300 -fill "#FFFFFF" `
        -annotate +0-100 "Job" `
        -pointsize 200 -fill "#B0B0B0" `
        -annotate +0+100 "Search" `
        assets\splash\splash_logo_dark.png
    
    Write-Host "[OK] Placeholder images created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: flutter pub get" -ForegroundColor White
    Write-Host "  2. Run: flutter pub run flutter_launcher_icons" -ForegroundColor White
    Write-Host "  3. Run: flutter pub run flutter_native_splash:create" -ForegroundColor White
    Write-Host ""
    Write-Host "IMPORTANT: Replace these placeholder images with professional" -ForegroundColor Yellow
    Write-Host "designs before production release!" -ForegroundColor Yellow
    
} else {
    Write-Host "[INFO] ImageMagick not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual Setup Required:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Create these PNG files:" -ForegroundColor White
    Write-Host "  1. assets\icons\app_icon.png (1024x1024)" -ForegroundColor White
    Write-Host "  2. assets\icons\app_icon_foreground.png (1024x1024)" -ForegroundColor White
    Write-Host "  3. assets\splash\splash_logo.png (1024x1024)" -ForegroundColor White
    Write-Host "  4. assets\splash\splash_logo_dark.png (1024x1024)" -ForegroundColor White
    Write-Host ""
    Write-Host "Design Tools:" -ForegroundColor Cyan
    Write-Host "  - Figma: https://www.figma.com/" -ForegroundColor White
    Write-Host "  - Canva: https://www.canva.com/" -ForegroundColor White
    Write-Host "  - GIMP (free): https://www.gimp.org/" -ForegroundColor White
    Write-Host ""
    Write-Host "Quick Placeholder:" -ForegroundColor Cyan
    Write-Host "  Use any image editor to create simple images with:" -ForegroundColor White
    Write-Host "  - Your app initials (JS for Job Search)" -ForegroundColor White
    Write-Host "  - Brand colors: #4A90E2 (blue)" -ForegroundColor White
    Write-Host ""
    Write-Host "After creating images, run:" -ForegroundColor Cyan
    Write-Host "  flutter pub get" -ForegroundColor White
    Write-Host "  flutter pub run flutter_launcher_icons" -ForegroundColor White
    Write-Host "  flutter pub run flutter_native_splash:create" -ForegroundColor White
    Write-Host ""
}
