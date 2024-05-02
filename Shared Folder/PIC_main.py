import subprocess
import threading
import time

def run_tcpdump(interface, output_file):
    def target():
        time.sleep(5)  # Delay the start of tcpdump
        subprocess.Popen(['tcpdump', '-i', interface, '-w', output_file])
    threading.Thread(target=target).start()

def run_script(script_path):
    def target():
        subprocess.Popen(['python', script_path])
    threading.Thread(target=target).start()

# Call PIC_Layout.py
run_script('PIC_Layout.py')

# Start two tcpdump instances after a delay
time.sleep(3)  # Wait for the script to start
print('tcpdump -D:')
subprocess.Popen(['tcpdump', '-D'])
run_tcpdump('s1-eth1', 'output1.pcap')
run_tcpdump('s1-eth2', 'output2.pcap')
run_tcpdump('s1-eth3', 'output3.pcap')
run_tcpdump('s1-eth4', 'output4.pcap')
run_tcpdump('s1', 'output5.pcap')
