[Setup]
AppName=Central de Contas Trans Helo
AppVersion=1.0
DefaultDirName={autopf}\Central de Contas Trans Helo
DefaultGroupName=Central de Contas Trans Helo
OutputDir=dist
OutputBaseFilename=Instalador_CentralTransHelo
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\CentralTransHelo.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Central de Contas Trans Helo"; Filename: "{app}\CentralTransHelo.exe"
Name: "{commondesktop}\Central de Contas Trans Helo"; Filename: "{app}\CentralTransHelo.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Opções adicionais:"
