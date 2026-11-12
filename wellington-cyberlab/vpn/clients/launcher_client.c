// ==============================================================================
// Wellington CyberLab — Windows Native PE32+ Launcher (x86-64)
// Compilado diretamente para Windows sem runtime pesado.
// ==============================================================================

__declspec(dllimport) int WinExec(const char* lpCmdLine, int uCmdShow);
__declspec(dllimport) void ExitProcess(int uExitCode);
__declspec(dllimport) int MessageBoxA(void* hWnd, const char* lpText, const char* lpCaption, unsigned int uType);

void WinMainCRTStartup(void) {
    // 1. Tentar executar o cliente via pythonw na pasta oficial C:\WellingtonCyberLab\bin
    // Comando tenta rodar via pythonw ou pyw silenciosamente (SW_HIDE = 0)
    const char* cmd1 = "cmd.exe /c \"if exist \"C:\\WellingtonCyberLab\\bin\\wellington_client_win.pyw\" (start \"\" pythonw \"C:\\WellingtonCyberLab\\bin\\wellington_client_win.pyw\") else if exist \"wellington_client_win.pyw\" (start \"\" pythonw \"wellington_client_win.pyw\") else (start \"\" pythonw bin\\wellington_client_win.pyw)\"";

    int res = WinExec(cmd1, 0);

    // Se WinExec falhou (< 31 significa erro no WinExec do Windows)
    if (res < 32) {
        MessageBoxA(0, 
            "O Python ou o arquivo do Wellington CyberLab nao foi localizado.\n\n"
            "Certifique-se de que o Python 3 esteja instalado no Windows com a opcao 'Add Python to PATH'.", 
            "Wellington CyberLab Client", 
            0x10 /* MB_ICONERROR */);
    }

    ExitProcess(0);
}
