; Inno Setup script for Anaxcel. Built by build.ps1 (ISCC.exe installer\anaxcel.iss /DAppVersion=x.y.z).
#ifndef AppVersion
  #define AppVersion "2.0.0"
#endif
#define AppName "Anaxcel"
#define AppExe  "Anaxcel.exe"

[Setup]
AppId={{6E1B7C52-3F7A-4C1E-9B8D-A2E5C0F4D9A1}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Mohamed Gueni
AppPublisherURL=https://github.com/Gueni/
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=Anaxcel-{#AppVersion}-Setup
SetupIconFile=..\assets\icons\icon_iEd_1.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\Anaxcel\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\data\defects_*";   DestDir: "{app}\samples"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autoprograms}\{#AppName} sample data"; Filename: "{app}\samples"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
