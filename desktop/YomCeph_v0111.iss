#define MyAppName "YomCeph Desktop"
#define MyAppVersion "0.11.1"
#define MyAppPublisher "YomCeph"
#define MyAppExeName "YomCeph_Desktop.exe"

[Setup]
AppId={{B8F36D2E-02D1-4BAA-A580-4B188B1488E8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\YomCeph Desktop
DefaultGroupName=YomCeph Desktop
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\installer
OutputBaseFilename=YomCeph_Desktop_Setup_v0.11.1
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=yomceph.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "..\dist\YomCeph_Desktop\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\YomCeph Desktop"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\YomCeph Desktop"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir YomCeph Desktop"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; La base de investigación NO se elimina al actualizar/desinstalar.
; Permanece en %LOCALAPPDATA%\YomCeph\ResearchData.
Type: filesandordirs; Name: "{app}"
