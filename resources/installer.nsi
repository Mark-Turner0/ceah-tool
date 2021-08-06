!include "MUI2.nsh"

;Information
Name "Cyber Essentials at Home Installer"
OutFile "Cyber-Essentials-at-Home-Installer.exe"
Unicode True
InstallDir "$LocalAppdata\Programs\Cyber Essentials at Home"

;License text
LicenseData "license.txt"

;Icons
!define MUI_ICON "..\imgs\logo.ico"
!define MUI_UNICON "..\imgs\logo.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "installerbitmap.bmp"

;Version Information
VIProductVersion "1.1"

;Allow write to registries
RequestExecutionLevel user


;Welcome Page settings
!define MUI_WELCOMEPAGE_TITLE "Thank you for participating!"
!define MUI_WELCOMEPAGE_TEXT "This installer will guide you through the installation process."

;License Page Settings
!define MUI_LICENSEPAGE_TEXT_TOP "Please accept the following participation agreement:"

;Installation Page Settings
!define MUI_INSTFILESPAGE_FINISHHEADER_TEXT "Installation Complete!"
!define MUI_INSTFILESPAGE_FINISHHEADER_SUBTEXT "Click next!"
!define MUI_ABORTWARNING
!define MUI_INSTFILESPAGE_ABORTHEADER_TEXT "Installation aborted"
!define MUI_INSTFILESPAGE_ABORTHEADER_SUBTEXT "Please restart the installer"

;Finish Page settings
!define MUI_FINISHPAGE_TITLE "Thank you for installing!"
!define MUI_FINISHPAGE_TEXT "On the next screen you will be asked to enter your unique 10 digit code that you received with your email invite to download the software."
!define MUI_FINISHPAGE_BUTTON "Next >"
!define MUI_FINISHPAGE_RUN "$INSTDIR\Cyber Essentials at Home.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Keep this box checked to go onto the next stage"
!define MUI_FINISHPAGE_NORETBOOTSUPPORT

;Uninstall Confirm Page settings
!define MUI_UNCONFIRMPAGE_TEXT_TOP "Are you sure you wish to withdraw? You can always email me at mark.turner-7@postgrad.manchester.ac.uk if you have any concerns"

;--------------------------------

;Installation pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

;Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;Language information
!insertmacro MUI_LANGUAGE "English"

;--------------------------------

;Installer
Section "Install"

  ExecWait 'TaskKill /IM "Cyber Essentials at Home.exe" /F'

  ;Set output path to the installation directory.
  SetOutPath $INSTDIR

  ;Files to be installed
  File /r "..\dist\Cyber Essentials at Home\*"

  ;Write registries so it shows up in "Add / Remove Programs"
  SetRegView 64
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Essentials at Home" "DisplayName" "Cyber Essentials at Home"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Essentials at Home" "UninstallString" "$\"$INSTDIR\Cyber Essentials at Home Uninstaller.exe$\""
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Essentials at Home" "DisplayIcon" "$\"$INSTDIR\imgs\logo.ico$\""
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Essentials at Home" "DisplayVersion" "1.1"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Essentials at Home" "NoModify" "1"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Essentials at Home" "EstimatedSize" "46000"

  ;Make sure program runs on startup
  SetShellVarContext current
  CreateShortcut "$SMSTARTUP\Cyber Essentials at Home.lnk" "$INSTDIR\Cyber Essentials at Home.exe"

  ;Create Uninstaller
  WriteUninstaller "$INSTDIR\Cyber Essentials at Home Uninstaller.exe"

SectionEnd

;--------------------------------

;Uninstaller

Section "Uninstall"

        ExecWait 'TaskKill /IM "Cyber Essentials at Home.exe" /F'

        ;Change working directory
        SetOutPath $TEMP

        ;Delete the installation directory
        RMDIR /r $INSTDIR

        ;Delete registries
        SetRegView 64
        DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Cyber Essentials at Home"
        DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Run\Cyber Essentials at Home"

        ;Delete startup link
        SetShellVarContext current
        Delete "$SMSTARTUP\Cyber Essentials at Home.lnk"

SectionEnd
