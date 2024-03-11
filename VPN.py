import random
import subprocess
import time
import pyperclip

data = str(random.randint(10, 2000)) + 'wobushijianben' + str(random.randint(10, 2000)) + '@163.com'
pyperclip.copy(data)
print(data)
# cd = r'cd D:\leidian\LDPlayer9'
# result = subprocess.run(cd, shell=True, check=True)
# print(result)
subprocess.run(r'D:\leidian\LDPlayer9\VPN.bat', shell=True, check=True)
time.sleep(200)
