# coding=utf-8

import RPi.GPIO as GPIO
import time, random, math, threading, paramiko, datetime, locale, yaml
# Ännu oanvänt bibliotek för att kontrollera temperatur på cpu på Raspberry Pi
# from gpiozero import CPUTemperature
from time import strftime
from datetime import datetime, timedelta, timezone
from ics import *
import urllib.request
import Adafruit_CharLCD as LCD # För LCD-skärm 2x16

locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')

# Laddar credentials
conf = yaml.load(open("credentials.yml"))

### GPIO och variabler för input och output pins ###

GPIO.setmode(GPIO.BCM)

#LCD-skärm
lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 2

lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)


#LED och swtichar
red_pin = 4
green_pin = 6
blue_pin = 5
red_switch_pin = 12
yellow_switch_pin = 13
white_switch_pin = 27

GPIO.setup(red_pin, GPIO.OUT)
GPIO.setup(green_pin, GPIO.OUT)
GPIO.setup(blue_pin, GPIO.OUT)
GPIO.setup(red_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(yellow_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(white_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Ännu oanvänd variable för att kontrollera temperatur på cpu på RaspberryPi
# cpu = CPUTemperature()

statusCal = "nada"
statusDay = "nada"
override = 0

### HTML och CSS - Variabler för skapande av index.html och style.css ###

indexHTML1 = '<html>\n<head>\n<meta charset="utf-8">\n<title>B212A - Mickes Rum - Ledigt eller Upptaget?</title>\n<meta name="description" content="B212A - Mickes rum - Upptaget eller ledigt?">\n<meta name="author" content="Micke Kring">\n<meta http-equiv="cache-control" content="no-cache, must-revalidate, post-check=0, pre-check=0" />\n<meta http-equiv="cache-control" content="max-age=0" />\n<meta http-equiv="expires" content="0" />\n<meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />\n<meta http-equiv="pragma" content="no-cache" />\n<meta http-equiv="refresh" content="12" />'
indexHTML2 = '\n<link rel="stylesheet" type="text/css" href="style.css">\n<link rel="stylesheet" type="text/css" href="style_bg.css">\n<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.1/css/all.css" integrity="sha384-mzrmE5qonljUremFsqc01SB46JvROS7bZs3IO2EmfFsd15uHvIt+Y8vEf7N7fWAU" crossorigin="anonymous">\n</head>\n'
indexHTML3 = '<body>\n<div class="list-row">\n<div class="list-left">'
indexHTML4 = '\n<div class="info"><h4><i class="far fa-envelope"></i> E-post | micke.kring@stockholm.se</h4><h4><i class="far fa-envelope"></i> E-post helpdesk | helpdesk@arstaskolan.se</h4><h4><i class="fa fa-question-circle" aria-hidden="true"> </i> Helpdesk portal | helpdesk.arstaskolan.se</h4></div>\n</div>\n<div class="list-right"><h3><i class="fab fa-rebel" aria-hidden="true"></i> RUM B212A</h3>'
indexHTML5 = '</div>\n<div class="list-right2"><h3><i class="fa fa-user" aria-hidden="true"></i> MICKE KRING</h3><p><img class="center" src="micke.jpg" width="250px" align="center"></p><h5>IT-pedagog | Årstaskolan</h5></div></div>\n</body>\n</html>'

roomStatus = 'nada'
roomTemp = 'nada'

### Thermistor - kod för att mäta temperaturen ###

C = 0.38 # uF - Tweek this value around 0.33 to improve accuracy
R1 = 1000 # Ohms
B = 3800.0 # The thermistor constant - change this for a different thermistor
R0 = 1000.0 # The resistance of the thermistor at 25C -change for different thermistor

a_pin = 8
b_pin = 7

def discharge():
	GPIO.setup(a_pin, GPIO.IN)
	GPIO.setup(b_pin, GPIO.OUT)
	GPIO.output(b_pin, False)
	time.sleep(0.01)

def charge_time():
	GPIO.setup(b_pin, GPIO.IN)
	GPIO.setup(a_pin, GPIO.OUT)
	GPIO.output(a_pin, True)
	t1 = time.time()
	while not GPIO.input(b_pin):
		pass
	t2 = time.time()
	return (t2 - t1) * 1000000

def analog_read():
	discharge()
	t = charge_time()
	discharge()
	return t

def read_resistance():
	n = 10
	total = 0;
	for i in range(0, n):
		total = total + analog_read()
	t = total / float(n)
	T = t * 0.632 * 3.3
	r = (T / C) - R1
	return r

def read_temp_c():
	R = read_resistance()
	t0 = 273.15     # 0 deg C in K
	t25 = t0 + 25.0 # 25 deg C in K
	# Steinhart-Hart equation - Google it
	inv_T = 1/t25 + 1/B * math.log(R/R0)
	T = (1/inv_T - t0)
	return T

### Färger för RGB-dioden ###

def green():
	GPIO.output(green_pin, True)
	GPIO.output(red_pin, False)
	GPIO.output(blue_pin, False)

def red():
	GPIO.output(green_pin, False)
	GPIO.output(red_pin, True)
	GPIO.output(blue_pin, False)

def blue():
	GPIO.output(blue_pin, True)
	GPIO.output(green_pin, False)
	GPIO.output(red_pin, False)

def off():
	GPIO.output(green_pin, False)
	GPIO.output(red_pin, False)
	GPIO.output(blue_pin, False)

### Threads / Trådar - Temperatur som kontinuerligt ska mätas oberoende av övriga programmet ###

def thread_start():
	while True:

		global tempFormat
		global roomTemp

		Calendar()

		tempCel = read_temp_c()
		tempFormat = "{:.1f}".format(tempCel)
		print("Temperatur inne: " + tempFormat + "\n")

		if tempFormat < "19.0":
			roomTemp = '<h2><i class="far fa-clock" aria-hidden="true"></i> ' + klNu + '</h2><h6>' + str(statusCal) + '</h6><br />' + '<h2><i class="fa fa-thermometer-quarter" aria-hidden="true"></i> Temperatur: ' + tempFormat + '°</h2><h6>Brrrrr. Oj, vad kallt det är.</h6>'
			with open("index2.html", "w") as f1:
				f1.write(indexHTML1 + indexHTML2 + indexHTML3 + roomStatus + indexHTML4 + roomTemp + indexHTML5)
			fileupload()

		elif tempFormat > "23.5":
			roomTemp = '<h2><i class="far fa-clock" aria-hidden="true"></i> ' + klNu + '</h2><h6>' + str(statusCal) + '</h6><br />' + '<h2><i class="fa fa-thermometer-full" aria-hidden="true"></i> Temperatur: ' + tempFormat + '°</h2><h6>Här är det varmt och svettigt nu.</h6>'
			with open("index2.html", "w") as f1:
				f1.write(indexHTML1 + indexHTML2 + indexHTML3 + roomStatus + indexHTML4 + roomTemp + indexHTML5)
			fileupload()

		else:
			roomTemp = '<h2><i class="far fa-clock" aria-hidden="true"></i> ' + klNu + '</h2><h6>' + str(statusCal) + '</h6><br />' + '<h2><i class="fa fa-thermometer-half" aria-hidden="true"></i> Temperatur: ' + tempFormat + '°</h2><h6>Just nu en rätt behaglig temperatur.</h6>'
			with open("index2.html", "w") as f1:
				f1.write(indexHTML1 + indexHTML2 + indexHTML3 + roomStatus + indexHTML4 + roomTemp + indexHTML5)
			fileupload()
			
		time.sleep(60)

### Klocka och tid - på skärm ###

def klockan():
	global klNu
	klNu = ("Kl " + strftime("%H:%M"))

### HTML och CSS vid upptaget, välkommen och ingen inne ###

def upptaget():
	global roomStatus
	if override == 0:
		lcd.clear()
		lcd.set_cursor(0, 0)
		lcd.message("UPPTAGET     AUT")
		lcd.set_cursor(0, 1)
		lcd.message(klNu + " | " + tempFormat +"C")
	else:
		lcd.clear()
		lcd.set_cursor(0, 0)
		lcd.message("UPPTAGET     MAN")
		lcd.set_cursor(0, 1)
		lcd.message(klNu + " | " + tempFormat +"C")
	roomStatus = ('<h1>UPPTAGET</h1><br /><p>Skicka ett mejl eller återkom senare.<br /><br /><i class="far fa-calendar-alt" aria-hidden="true"></i> Kalender</p><br /><h6>' + statusDay + '</h6></p>')
	css = ('body{background-color: #d63535;}')

	with open("style_bg.css", "w") as f1, open("index2.html", "w") as f2:
		f1.write(css)
		f2.write(indexHTML1 + indexHTML2 + indexHTML3 + roomStatus + indexHTML4 + roomTemp + indexHTML5)
	fileupload()

def valkommen():
	global roomStatus
	if override == 0:
		lcd.clear()
		lcd.set_cursor(0, 0)
		lcd.message("VALKOMMEN    AUT")
		lcd.set_cursor(0, 1)
		lcd.message(klNu + " | " + tempFormat +"C")
	else:
		lcd.clear()
		lcd.set_cursor(0, 0)
		lcd.message("VALKOMMEN    MAN")
		lcd.set_cursor(0, 1)
	roomStatus = ('<h1>VÄLKOMMEN</h1><br /><p>Knacka på och stig in.<br /><br /><i class="far fa-calendar-alt" aria-hidden="true"></i> Kalender</p><br /><h6>' + statusDay + '</h6></p>')
	css = ('body{background-color: #52a530;}')

	with open("style_bg.css", "w") as f1, open("index2.html", "w") as f2:
		f1.write(css)
		f2.write(indexHTML1 + indexHTML2 + indexHTML3 + roomStatus + indexHTML4 + roomTemp + indexHTML5)
	fileupload()

def ingeninne():
	global roomStatus
	if override == 0:
		lcd.clear()
		lcd.set_cursor(0, 0)
		lcd.message("INGEN INNE   AUT")
		lcd.set_cursor(0, 1)
		lcd.message(klNu + " | " + tempFormat +"C")
	else:
		lcd.clear()
		lcd.set_cursor(0, 0)
		lcd.message("INGEN INNE   MAN")
		lcd.set_cursor(0, 1)
	roomStatus = ('<h1>INGEN INNE</h1><br /><p>Rummet är tomt.<br /><br /><i class="far fa-calendar-alt" aria-hidden="true"></i> Kalender</p><br /><h6>' + statusDay + '</h6></p>')
	css = ('body{background-color: #333333;}')

	with open("style_bg.css", "w") as f1, open("index2.html", "w") as f2:
		f1.write(css)
		f2.write(indexHTML1 + indexHTML2 + indexHTML3 + roomStatus + indexHTML4 + roomTemp + indexHTML5)
	fileupload()

### Uppladdning av filer - via sftp. (Inte samma som ftp.) ###

def fileupload(): # Här laddar vi upp filerna som har med välkommen, upptaget och ingen inne att göra
	try:
		host = conf['user']['host']
		port = conf['user']['port']
		transport = paramiko.Transport((host, port))

		password = conf['user']['password']
		username = conf['user']['username']
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		sftp.chdir("/var/www/bloggmu/public/rum/")
		filepath = "index2.html"
		localpath = "/home/pi/Micke/index2.html"
		filepath2 = "style.css"
		localpath2 = "/home/pi/Micke/style.css"
		filepath3 = "style_bg.css"
		localpath3 = "/home/pi/Micke/style_bg.css"

		sftp.put(localpath, filepath)
		sftp.put(localpath2, filepath2)
		sftp.put(localpath3, filepath3)

		sftp.close()
		transport.close()
		print("Filerna har laddats upp.")
	except:
		print("Error. Filerna kunde inte laddas upp.")
		pass

def indexupload(): # Här laddar vi upp alla initiala filer som behövs som inte uppdateras under körning.
	try:
		host = conf['user']['host']
		port = conf['user']['port']
		transport = paramiko.Transport((host, port))

		password = conf['user']['password']
		username = conf['user']['username']
		transport.connect(username = username, password = password)

		sftp = paramiko.SFTPClient.from_transport(transport)

		sftp.chdir("/var/www/bloggmu/public/rum/")
		filepath5 = "index2.html"
		localpath5 = "/home/pi/Micke/index2.html"
		filepath6 = "style.css"
		localpath6 = "/home/pi/Micke/style.css"
		filepath7 = "user_pic.jpg"
		localpath7 = "/home/pi/Micke/micke.jpg"
		filepath8 = "style_bg.css"
		localpath8 = "/home/pi/Micke/style_bg.css"
		filepath9 = "index.html"
		localpath9 = "/home/pi/Micke/index.html"

		sftp.put(localpath5, filepath5)
		sftp.put(localpath6, filepath6)
		sftp.put(localpath7, filepath7)
		sftp.put(localpath8, filepath8)
		sftp.put(localpath9, filepath9)

		sftp.close()
		transport.close()
	except:
		print("Error. Filerna kunde inte laddas upp.")
		pass

def Calendar():
	global statusCal
	global statusDay
	global override
	klockan()

	url = conf['urlcalendar']['link_url']

	with urllib.request.urlopen(url) as response:
		ics_string = response.read()

	### RIGHT NOW ###

	window_start = datetime.now(timezone.utc)
	window_end = window_start + timedelta(minutes=1)
	events = get_events_from_ics(ics_string, window_start, window_end)

	for e in events:
		activity_now = ('{}'.format(e['summary']))
		room_now = ('{}'.format(e['loc']))
		start = (e['startdt'])
		start_date = (start.strftime("%Y-%m-%d"))
		start_time = (start.strftime("%H:%M"))
		end = (e['enddt'])
		end_date = (end.strftime("%Y-%m-%d"))
		end_time = (end.strftime("%H:%M"))

	try:
		if override == 0:
			if "möte" in activity_now.lower():
				print("UPPTAGET!")
				red()
				upptaget()
			elif "semester" in activity_now.lower() or "ledig" in activity_now.lower() or "lunch" in activity_now.lower():
				print("INGEN INNE")
				off()
				ingeninne()
			else:
				print("VÄLKOMMEN")
				green()
				valkommen()
				pass
		else:
			pass

		statusCal = ((start_time) + " - " + (end_time) + " | " + (activity_now) + "<br />Plats: " + (room_now.upper()))
		print(statusCal)

	except:
		statusCal = ("Inget i kalendern nu<br />Plats: Okänd")
		print(statusCal)

	### LIST 24 HRS ###

	window_start = datetime.now(timezone.utc)
	window_end = window_start + timedelta(hours=18)
	events = get_events_from_ics(ics_string, window_start, window_end)

	listDay = []

	for e in events:
		activity_day = ('{}'.format(e['summary']))
		room_day = ('{}'.format(e['loc']))
		start = (e['startdt'])
		start_date_day = (start.strftime("%a"))
		start_time_day = (start.strftime("%H:%M"))
		end  = (e['enddt'])
		end_date_day = (end.strftime("%Y-%m-%d"))
		end_time_day = (end.strftime("%H:%M"))
		listDay.append((start_date_day.capitalize()) + " // " + (start_time_day) + " - " + (end_time_day) + " // " + (activity_day) + "<br />")
	statusDay = ("".join(listDay))
	print(statusDay)

def Main():

	try:
		global override
		button_delay = 0.2
		off()
		lcd.clear()
		lcd.message("Bootar system...")
		print("\nBootar systemet...")
		time.sleep(2.0)
		lcd.clear()
		lcd.message("Startar tråd...")
		t1 = threading.Thread(target = thread_start)
		t1.start()
		
		print("\nLaddar upp initiala filer...")
		time.sleep(1.0)
		lcd.clear()
		lcd.message("Uploading files...")
		indexupload() # Laddar upp alla filer som initialt behövs, i fall lokala ändringar gjorts
		time.sleep(2.0)
		lcd.clear()
		lcd.message("Ready player one")
		print("\nRedo att tjäna!!!")
		
		while True:
		
			if GPIO.input(red_switch_pin) == False:
				time.sleep(button_delay)
				if override == 0:
					override = 1
					red()
					upptaget()
				else:
					for blink in range(0,2):
						blue()
						time.sleep(0.2)
						blue()
						time.sleep(0.2)
						blue()
						time.sleep(0.2)
						off()
					override = 0

			if GPIO.input(yellow_switch_pin) == False:
				time.sleep(button_delay)
				if override == 0:
					override = 1
					green()
					valkommen()
				else:
					for blink in range(0,2):
						blue()
						time.sleep(0.2)
						blue()
						time.sleep(0.2)
						blue()
						time.sleep(0.2)
						off()
					override = 0

			if GPIO.input(white_switch_pin) == False:
				time.sleep(button_delay)
				if override == 0:
					override = 1
					for blink in range(0,2):
						blue()
						time.sleep(0.2)
						blue()
						time.sleep(0.2)
						blue()
						time.sleep(0.2)
						off()
					ingeninne()
				else:
					for blink in range(0,2):
						blue()
						time.sleep(0.2)
						blue()
						time.sleep(0.2)
						blue()
						time.sleep(0.2)
						off()
					override = 0
	
	finally: # Om programmet avslutas rensas GPIO
		print("Rensar...")
		lcd.clear()
		GPIO.cleanup()

### MAIN PROGRAM ###

if __name__ == "__main__":
	Main()