#define MyAppName "Flowizi"
#define MyAppVersion "0.4.0-alpha"
#define MyAppPublisher "Jean Giraldo"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{D9EE3998-39C8-4B75-AF64-31FF4ACAD74C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=C:\Users\jeanp\Desktop
OutputBaseFilename={#MyAppName} {#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[VersionInfo]
FileVersion={#MyAppVersion}

[Files]
Source: "C:\Users\jeanp\Desktop\flowizi.exe"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "Path"; ValueData: "{olddata};{app}"; Flags: uninsdeletevalue;
