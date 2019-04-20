from bluepy.btle import Scanner, DefaultDelegate

scanner = Scanner()
devices = scanner.scan(1.0)

for dev in devices:
    for (adtype, desc, value) in dev.getScanData():
        # print("  %s = %s" % (desc, value))
        if desc == 'Complete Local Name' and value.find('IM-100K') > -1:
            print(value)
            print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))

