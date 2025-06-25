import os
import re
import cv2
import sys
import paramiko
import numpy as np

from typing import List
from fnmatch import fnmatch


class RemoteConnection:
    def __init__(self, 
                 hostname: str,
                 port: int,
                 username: str,
                 password: str):

        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self._connected = False

    def __del__(self):
        self.ssh_disconnect()
    
    @property
    def hostname(self) -> str:
        return self.__hostname
    
    @property
    def port(self) -> int:
        return self.__port
    
    @property
    def username(self) -> str:
        return self.__username
    
    @property
    def password(self) -> str:
        return self.__password
    
    @hostname.setter
    def hostname(self, value: str):
        if not isinstance(value, str) or not value:
            raise ValueError("hostname должен быть непустой строкой")
        
        self.__hostname = value
    
    @port.setter
    def port(self, value: int):
        if not isinstance(value, int) or not (0 < value < 65536):
            raise ValueError("port должен быть числом от 1 до 65535")
        
        self.__port = value
    
    @username.setter
    def username(self, value: str):
        if not isinstance(value, str) or not value:
            raise ValueError("username должен быть непустой строкой")
        
        self.__username = value
    
    @password.setter
    def password(self, value: str):
        if not isinstance(value, str):
            raise ValueError("password должен быть строкой")
        
        self.__password = value

    def _match_pattern(self, filename: str, pattern: str) -> bool:
        pattern = pattern.strip()
        if pattern == "*":
            return True
        if pattern.startswith("*."):
            return fnmatch(filename, pattern)
        if "." in pattern:
            return fnmatch(filename, pattern)
        return filename == pattern

    def _print_progress_bar(self, 
                        current: int, 
                        total: int, 
                        prefix: str = "", 
                        bar_width: int = 10):
        percent = int(current / total * 100) if total > 0 else 100
        blocks = int(percent / (100 / bar_width))
        bar = "█" * blocks + "-" * (bar_width - blocks)
        sys.stdout.write(f"\r{prefix} [{bar}] {percent}% ({current}/{total} bytes)")
        sys.stdout.flush()



    def ssh_connect(self) -> None:
        if self._connected:
            return

        self._ssh.connect(
            hostname=self.__hostname,
            port=self.__port,
            username=self.__username,
            password=self.__password
        )
        self._connected = True
        print(f"✅ Установлено SSH-соединение с {self.__hostname}")

    def ssh_disconnect(self) -> None:
        if self._connected:
            self._ssh.close()
            self._connected = False
            print(f"🔌 SSH-соединение с {self.__hostname} закрыто")
    
    def search_files(self,
                     remote_dir: str,
                     extensions: List[str]) -> List[str]:
        
        if not self._connected:
            self.ssh_connect()

        if not extensions:
            raise ValueError("Список расширений не должен быть пустым")
        
        ext_cond = " -o ".join([f"-iname '*.{ext.lstrip('.')}'" for ext in extensions])
        find_command = f"find {remote_dir} '(' {ext_cond} ')'"

        stdin, stdout, stderr = self._ssh.exec_command(find_command)
        output = stdout.read().decode().splitlines()
        errors = stderr.read().decode()

        if errors:
            print("⚠️ Ошибки при поиске файлов:", errors)

        return output

    def download_files(self, 
                       remote_dir: str, 
                       local_dir: str, 
                       pattern: str = "*") -> None:
        
        if not self._connected:
            self.ssh_connect()

        sftp = self._ssh.open_sftp()
        os.makedirs(local_dir, exist_ok=True)

        try:
            files = sftp.listdir(remote_dir)
        except IOError as e:
            print(f"❌ Ошибка доступа к {remote_dir}: {e}")
            return

        matched_files = [f for f in files if self._match_pattern(f, pattern)]

        total_bytes = 0
        file_sizes = {}
        for filename in matched_files:
            try:
                file_path = os.path.join(remote_dir, filename)
                size = sftp.stat(file_path).st_size
                total_bytes += size
                file_sizes[filename] = size
            except IOError:
                continue

        if total_bytes == 0:
            print("⚠️ Нет доступных файлов для скачивания.")
            return

        downloaded_bytes = 0

        for filename in matched_files:
            remote_path = os.path.join(remote_dir, filename)
            local_path = os.path.join(local_dir, filename)

            try:
                with sftp.open(remote_path, "rb") as remote_file, open(local_path, "wb") as local_file:
                    chunk_size = 4096
                    while True:
                        data = remote_file.read(chunk_size)
                        if not data:
                            break
                        local_file.write(data)
                        downloaded_bytes += len(data)
                        self._print_progress_bar(downloaded_bytes, total_bytes, prefix="⬇️ Общая загрузка", bar_width=50)
            except IOError as e:
                print(f"\n⚠️ Ошибка при скачивании {filename}: {e}")

        print()  # Переход на новую строку
        sftp.close()



    def load_files(self, remote_dir: str, pattern: str = "*") -> dict:
        if not self._connected:
            self.ssh_connect()

        sftp = self._ssh.open_sftp()
        file_contents = {}

        try:
            files = sftp.listdir(remote_dir)
        except IOError as e:
            print(f"❌ Ошибка доступа к {remote_dir}: {e}")
            return {}

        matched_files = [f for f in files if self._match_pattern(f, pattern)]

        total_bytes = 0
        file_sizes = {}
        for filename in matched_files:
            try:
                size = sftp.stat(os.path.join(remote_dir, filename)).st_size
                total_bytes += size
                file_sizes[filename] = size
            except IOError:
                continue

        if total_bytes == 0:
            print("⚠️ Нет файлов для загрузки.")
            return {}

        read_bytes = 0

        for filename in matched_files:
            remote_path = os.path.join(remote_dir, filename)
            try:
                with sftp.open(remote_path, "rb") as remote_file:
                    chunk_size = 4096
                    buffer = bytearray()

                    while True:
                        data = remote_file.read(chunk_size)
                        if not data:
                            break
                        buffer.extend(data)
                        read_bytes += len(data)
                        self._print_progress_bar(read_bytes, total_bytes, prefix="📥 Общая загрузка", bar_width=50)

                    file_contents[filename] = bytes(buffer)

            except IOError as e:
                print(f"\n⚠️ Не удалось загрузить {remote_path}: {e}")

        print()
        sftp.close()
        return file_contents



if __name__ == "__main__":
    ssh = RemoteConnection(hostname="192.168.21.1",
                           port=22,
                           username="rnf",
                           password="12345678")
    
    files = ssh.search_files(remote_dir="/home/rnf/dev/ros2_iiwa_realsense_camera/images",
                             extensions=["jpg"])

    for f in files:
        print(f)

    ssh.download_files(remote_dir="/home/rnf/dev/ros2_iiwa_realsense_camera/images",
                       local_dir="/home/daniel/dev/docker_dev/web_service/calibration_module/images",
                       pattern="*")
    