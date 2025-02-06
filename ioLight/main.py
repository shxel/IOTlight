# main.py - Secure IoT Lighting Controller
import network
import utime
import ujson
from machine import Pin, RTC, Timer, WDT, reset
import ntptime
import usocket as socket
import ubinascii
import urequests
import ucryptolib
import uhashlib
import sys
import uos

# Configuration
CONFIG = {
    'wifi_ssid': 'YOUR_SSID',
    'wifi_pass': 'YOUR_PASS',
    'api_key': 'SECURE_KEY_' + ubinascii.hexlify(network.WLAN().config('mac')[-3:]).decode(),
    'max_runtime': 43200,  # 12 hours
    'timezone': 'UTC+2',
    'ota_url': 'https://your-ota-server.com/firmware'
}

class SecureLightingSystem:
    def __init__(self):
        self.wdt = WDT(timeout=30000)
        self.relay = Pin(12, Pin.OUT, value=0)
        self.rtc = RTC()
        self.network = NetworkManager()
        self.scheduler = ScheduleManager()
        self.ota = OTAManager(CONFIG['ota_url'])
        self.api = APIServer(self)
        self.last_activity = utime.time()

    def run(self):
        self.network.connect()
        self.scheduler.load()
        self.ota.check_update()
        self.api.start_server()
        self.main_loop()

    def main_loop(self):
        timer = Timer(-1)
        timer.init(period=60000, mode=Timer.PERIODIC, callback=lambda t: (
            self.wdt.feed(),
            self.scheduler.check_schedule(),
            self.check_inactivity()
        ))
        while True:
            self.api.handle_clients()
            utime.sleep_ms(100)

    def check_inactivity(self):
        if utime.time() - self.last_activity > 86400:  # 24h
            reset()

class NetworkManager:
    def __init__(self):
        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)
        self.mac = ubinascii.hexlify(network.WLAN().config('mac')).decode()

    def connect(self):
        self.sta.active(True)
        self.sta.connect(CONFIG['wifi_ssid'], CONFIG['wifi_pass'])
        for _ in range(15):
            if self.sta.isconnected():
                print(f'Connected: {self.sta.ifconfig()}')
                return True
        self.start_ap()
        return False

    def start_ap(self):
        self.ap.config(
            essid=f'LightCtrl-{self.mac[-6:]}',
            password='INIT_'+str(utime.time())[-4:],
            authmode=network.AUTH_WPA2_PSK
        )
        self.ap.active(True)

class ScheduleManager:
    def __init__(self):
        self.schedule = {'entries': [], 'enabled': True}
        self.crc = None

    def load(self):
        try:
            with open('schedule.json', 'r') as f:
                data = f.read()
                if self.verify_crc(data):
                    self.schedule = ujson.loads(data[:-8])
        except Exception as e:
            print(f'Schedule load error: {e}')

    def save(self, data):
        try:
            crc = ubinascii.hexlify(uhashlib.sha256(ujson.dumps(data)).digest()).decode()
            with open('schedule.json', 'w') as f:
                f.write(ujson.dumps(data) + crc)
            return True
        except Exception as e:
            print(f'Schedule save error: {e}')
            return False

    def verify_crc(self, data):
        if len(data) < 64: return False
        content, crc = data[:-64], data[-64:]
        return uhashlib.sha256(content).digest() == ubinascii.unhexlify(crc)

    def check_schedule(self):
        if not self.schedule['enabled']: return
        now = utime.localtime()
        current_min = now[3] * 60 + now[4]
        for entry in self.schedule['entries']:
            if now[6] in entry['days'] and entry['enabled']:
                start = entry['on'][0] * 60 + entry['on'][1]
                end = entry['off'][0] * 60 + entry['off'][1]
                if (start <= current_min < end) if start < end else (current_min >= start or current_min < end):
                    self.relay.on()
                    return
        self.relay.off()

class OTAManager:
    def __init__(self, url):
        self.url = url
        self.pub_key = b'-----BEGIN PUBLIC KEY-----\n...'  # Insert actual key

    def check_update(self):
        try:
            headers = {'X-Device-ID': CONFIG['api_key']}
            response = urequests.get(self.url, headers=headers)
            if self.verify_update(response.content, response.headers['X-Signature']):
                self.apply_update(response.content)
        except Exception as e:
            print(f'OTA error: {e}')

    def verify_update(self, data, signature):
        # Implement proper RSA verification
        return True  # Placeholder

    def apply_update(self, data):
        try:
            with open('firmware.tmp', 'wb') as f:
                f.write(data)
            uos.rename('firmware.tmp', 'main.py')
            reset()
        except Exception as e:
            print(f'Update failed: {e}')

class APIServer:
    def __init__(self, system):
        self.system = system
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 80))
        self.socket.listen(5)
        self.clients = []
        self.rate_limits = {}

    def start_server(self):
        print(f'API server started on port 80')

    def handle_clients(self):
        try:
            conn, addr = self.socket.accept()
            self.handle_request(conn)
            conn.close()
        except Exception as e:
            print(f'API error: {e}')

    def handle_request(self, conn):
        request = conn.recv(1024).decode()
        headers, _, body = request.partition('\r\n\r\n')
        lines = headers.split('\r\n')
        method, path, _ = lines[0].split()
        
        # Rate limiting
        client_ip = conn.getpeername()[0]
        if utime.time() - self.rate_limits.get(client_ip, 0) < 1:
            conn.send('HTTP/1.1 429 Too Many Requests\r\n\r\n')
            return
        
        # Authentication
        api_key = next((line.split(': ')[1] for line in lines if 'X-API-Key' in line), None)
        if api_key != CONFIG['api_key']:
            conn.send('HTTP/1.1 401 Unauthorized\r\n\r\n')
            return
        
        # Endpoint handling
        response = self.route_request(method, path, body)
        conn.send(response)
        self.rate_limits[client_ip] = utime.time()

    def route_request(self, method, path, body):
        # Endpoint implementation
        return 'HTTP/1.1 200 OK\r\n\r\nOK'

system = SecureLightingSystem()
system.run()