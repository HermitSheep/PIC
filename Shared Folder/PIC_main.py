import subprocess
import threading
import time

def run_tcpdump(interface, output_file):
    def target():
        #time.sleep(5)  # Delay the start of tcpdump
        subprocess.Popen(['tcpdump', '-i', interface, '-w', output_file, '-G', '171'])
    threading.Thread(target=target).start()

def run_script(script_path):
    def target():
        subprocess.Popen(['python', script_path])
    threading.Thread(target=target).start()

# Call PIC_Layout.py
run_script('PIC_Layout.py')

# Start two tcpdump instances after a delay
time.sleep(2)  # Wait for the script to start
print('tcpdump -D:')
subprocess.Popen(['tcpdump', '-D'])
run_tcpdump('s1-eth1', 'outS-h1.pcap')
run_tcpdump('s1-eth2', 'outS-h2.pcap')
run_tcpdump('s1-eth3', 'outS-ap1.pcap')
run_tcpdump('s1-eth4', 'outS-ap2.pcap')
run_tcpdump('ap1-wlan1', 'outAp1-w.pcap')
run_tcpdump('ap2-wlan1', 'outAp2-w.pcap')
run_tcpdump('hwsim0', 'outW.pcap')
run_tcpdump('docker0', 'outDocker.pcap')
run_tcpdump('lo', 'outLo.pcap')
