; Snakeverse Installer Script
; ----------------------------

!include "MUI2.nsh"

; ── Información del instalador ──
Name "Snakeverse"
OutFile "final\Snakeverse_Setup.exe"
InstallDir "$PROGRAMFILES\Snakeverse"
RequestExecutionLevel admin

; ── Configuración de la interfaz moderna ──
!define MUI_ABORTWARNING

; ── Páginas del instalador ──
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "licencia.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Spanish"

; ── Sección de instalación ──
Section "Instalar Snakeverse"
    SetOutPath "$INSTDIR"
    
    ; Copiar todos los archivos del juego
    File /r "dist\Snakeverse\*.*"
    
    ; Crear accesos directos
    CreateShortCut "$DESKTOP\Snakeverse.lnk" "$INSTDIR\Snakeverse.exe"
    CreateDirectory "$SMPROGRAMS\Snakeverse"
    CreateShortCut "$SMPROGRAMS\Snakeverse\Snakeverse.lnk" "$INSTDIR\Snakeverse.exe"
    CreateShortCut "$SMPROGRAMS\Snakeverse\Desinstalar Snakeverse.lnk" "$INSTDIR\uninstall.exe"
    
    ; Escribir información de desinstalación en el registro
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snakeverse" "DisplayName" "Snakeverse"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snakeverse" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snakeverse" "DisplayIcon" "$INSTDIR\Snakeverse.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snakeverse" "Publisher" "Snakeverse Team"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snakeverse" "DisplayVersion" "1.0"
    
    ; Crear desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; ── Sección de desinstalación ──
Section "Uninstall"
    ; Eliminar archivos y carpetas
    RMDir /r "$INSTDIR"
    
    ; Eliminar accesos directos
    Delete "$DESKTOP\Snakeverse.lnk"
    Delete "$SMPROGRAMS\Snakeverse\Snakeverse.lnk"
    Delete "$SMPROGRAMS\Snakeverse\Desinstalar Snakeverse.lnk"
    RMDir "$SMPROGRAMS\Snakeverse"
    
    ; Eliminar registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Snakeverse"
SectionEnd