#define UNICODE
#define _UNICODE

#include <cstdlib>
#include <cwchar>
#include <cstring>
#include <vector>
#include <string>
#include <iterator>

#include <windows.h>

int wmain(int argc, wchar_t *argv[], wchar_t *envp[])
{
    std::wstring arg1(L"python.exe cc.py");
    std::vector<wchar_t> command_line;
    std::copy(std::begin(arg1), std::end(arg1), std::back_inserter(command_line));
    for (int i = 1; i < argc; ++i)
    {
        command_line.push_back(L' ');
        std::copy(argv[i], argv[i] + wcslen(argv[i]), std::back_inserter(command_line));
    }
    command_line.push_back(0);

    ::STARTUPINFOW si;
    memset(&si, 0, sizeof(::STARTUPINFO));
    si.cb = sizeof(::STARTUPINFOW);

    ::PROCESS_INFORMATION pi;
    memset(&pi, 0, sizeof(::PROCESS_INFORMATION));

    BOOL status = ::CreateProcessW(nullptr,
        command_line.data(),
        nullptr,
        nullptr,
        TRUE,
        0,
        nullptr,
        nullptr,
        &si,
        &pi);
    if (!status)
        return EXIT_FAILURE;

    ::WaitForSingleObject(pi.hProcess, INFINITE);
    ::WaitForSingleObject(pi.hThread, INFINITE);

    DWORD exit_code(0);
    ::GetExitCodeProcess(pi.hProcess, &exit_code);

    ::CloseHandle(pi.hProcess);
    ::CloseHandle(pi.hThread);

    return static_cast<int>(exit_code);
}
