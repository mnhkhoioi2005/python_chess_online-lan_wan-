"""
NgrokHelper - Quản lý Ngrok tunnel
Tự động khởi động ngrok và lấy public URL
"""
import subprocess
import time
import requests
import json
import os
import sys

class NgrokHelper:
    def __init__(self):
        self.public_url = None
        self.process = None
        self.host = None
        self.port = None
        self.ngrok_path = self._find_ngrok()
    
    def _find_ngrok(self):
        """Tìm đường dẫn tới ngrok executable"""
        # 1. Thử trong PATH
        try:
            subprocess.run(['ngrok', 'version'], capture_output=True, check=True)
            return 'ngrok'
        except:
            pass
        
        # 2. Thử trong thư mục hiện tại
        current_dir = os.getcwd()
        ngrok_local = os.path.join(current_dir, 'ngrok.exe' if sys.platform == 'win32' else 'ngrok')
        if os.path.exists(ngrok_local):
            return ngrok_local
        
        # 3. Thử trong thư mục script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        ngrok_parent = os.path.join(parent_dir, 'ngrok.exe' if sys.platform == 'win32' else 'ngrok')
        if os.path.exists(ngrok_parent):
            return ngrok_parent
        
        return None
    
    def start_tunnel(self, port=12347):
        """
        Khởi động ngrok tunnel
        
        Args:
            port: Port local cần expose
            
        Returns:
            str: Public URL (format: "host:port") hoặc None nếu lỗi
        """
        print(f"Starting Ngrok tunnel for port {port}...")
        
        if not self.ngrok_path:
            print("ERROR: Ngrok not found!")
            print("Installation guide:")
            print("   1. Download: https://ngrok.com/download")
            print("   2. Extract ngrok.exe to this folder")
            print("   3. Run: ngrok authtoken YOUR_TOKEN")
            return None
        
        print(f"Using ngrok at: {self.ngrok_path}")
        
        try:
            # Chạy ngrok tcp
            self.process = subprocess.Popen(
                [self.ngrok_path, 'tcp', str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Check if process started successfully
            time.sleep(1)
            if self.process.poll() is not None:
                # Process exited immediately - likely auth error
                stdout, stderr = self.process.communicate()
                print("ERROR: Ngrok process exited immediately!")
                print(f"STDERR: {stderr.decode('utf-8', errors='ignore')}")
                print(f"STDOUT: {stdout.decode('utf-8', errors='ignore')}")
                print("\nPossible causes:")
                print("1. Ngrok auth token not configured")
                print("2. Run: ngrok authtoken YOUR_TOKEN")
                print("3. Get token from: https://dashboard.ngrok.com/get-started/your-authtoken")
                return None
            
            # Đợi ngrok khởi động
            print("Waiting for Ngrok to start (this may take 5-10 seconds)...")
            time.sleep(5)
            
            # Lấy public URL từ ngrok API
            public_url = self._get_public_url(max_retries=10)
            
            if public_url:
                self.public_url = public_url
                print(f"SUCCESS: Ngrok tunnel ready!")
                print(f"Public URL: {public_url}")
                return public_url
            else:
                print("ERROR: Could not get public URL from Ngrok")
                print("Check if ngrok auth token is configured:")
                print("  ngrok authtoken YOUR_TOKEN")
                self.stop_tunnel()
                return None
                
        except FileNotFoundError:
            print("ERROR: Ngrok not found!")
            print("Installation guide:")
            print("   1. Download: https://ngrok.com/download")
            print("   2. Extract and add to PATH")
            print("   3. Run: ngrok authtoken YOUR_TOKEN")
            return None
        except Exception as e:
            print(f"ERROR starting Ngrok: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_public_url(self, max_retries=10):
        """Lấy public URL từ Ngrok API"""
        print(f"Attempting to get public URL (max {max_retries} retries)...")
        
        for attempt in range(max_retries):
            try:
                print(f"  Attempt {attempt + 1}/{max_retries}...", end=" ")
                response = requests.get('http://localhost:4040/api/tunnels', timeout=3)
                data = response.json()
                
                if 'tunnels' in data and len(data['tunnels']) > 0:
                    tunnel = data['tunnels'][0]
                    public_url = tunnel['public_url']
                    print(f"SUCCESS!")
                    
                    # Format: tcp://0.tcp.ngrok.io:12345 -> 0.tcp.ngrok.io:12345
                    if public_url.startswith('tcp://'):
                        public_url = public_url.replace('tcp://', '')
                    
                    # Parse host và port
                    if ':' in public_url:
                        self.host, port_str = public_url.rsplit(':', 1)
                        self.port = int(port_str)
                    
                    return public_url
                else:
                    print(f"No tunnels found yet")
                    
            except requests.exceptions.ConnectionError:
                print(f"Connection refused (Ngrok API not ready)")
                if attempt < max_retries - 1:
                    time.sleep(1.5)
                    continue
            except Exception as e:
                print(f"Error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1.5)
        
        print("FAILED: Could not get public URL after all retries")
        return None
    
    def stop_tunnel(self):
        """Dừng ngrok tunnel"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
                print("Ngrok tunnel stopped")
            except:
                self.process.kill()
            finally:
                self.process = None
                self.public_url = None
    
    def is_running(self):
        """Check xem ngrok có đang chạy không"""
        return self.process is not None and self.process.poll() is None
    
    def get_url(self):
        """Lấy public URL hiện tại"""
        return self.public_url
    
    def __del__(self):
        """Cleanup khi object bị hủy"""
        self.stop_tunnel()


if __name__ == "__main__":
    # Test ngrok helper
    print("=== NGROK HELPER TEST ===")
    
    ngrok = NgrokHelper()
    url = ngrok.start_tunnel(12347)
    
    if url:
        print(f"\n✅ Thành công!")
        print(f"Public URL: {url}")
        print(f"Host: {ngrok.host}")
        print(f"Port: {ngrok.port}")
        
        input("\nNhấn Enter để dừng tunnel...")
        ngrok.stop_tunnel()
    else:
        print("\n❌ Không thể khởi động Ngrok")
