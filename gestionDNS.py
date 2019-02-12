import subprocess, sys, re
# para generacioń de IPs aleatorias
import random, socket, struct
# para verificar que existe fichero
import os.path

#file_dns='/var/cache/bind/ext-juanpe.gonzalonazareno.org'
file_dns='prueba-ext'
file_dns_inverso='/var/cache/bind/ext-200.22.172.in-addr.arpa'

## Para el caso de gestionar el DNS interno
#file_dns_int='/var/cache/bind/int-juanpe.gonzalonazareno.org'
#file_dns_inverso_int='/var/cache/bind/int-10.in-addr.arpa'

## Para comprobar que sea del mismo rango de ip
comprobar_red=True
rango_red='172.22.'

def mostrar_ayuda(accion=None,tipo=None):
	print('-- Ayuda gestionDNS --')
	if accion=='-a' or accion==None:
		print('\t-- Ayuda -a --> Añade un registro en el DNS')
		print('\tUso -a: python3 gestionDNS.py -a < -dir | -alias > <var1>  <var2>')		

		if tipo=='-dir':
			print('\t\t-- Ayuda -a -dir --> Añade un registro tipo A con nombre igual a <var1> e IP igual a <var2>')
			print('\t\tEj: python3 gestionDNS.py -a -dir nodo1 172.22.200.123')
		if tipo=='-alias':
			print('\t\t-- Ayuda -a -alias --> Añade un registro tipo CNAME con nombre igual a <var1> asociado al registro A <var2>')
			print('\t\tEj: python3 gestionDNS.py -a -alias www nodo1')

	if accion=='-b' or accion==None:
		print('\t-- Ayuda -b --> Borra un registro en el DNS')
		print('\tUso -b: python3 gestionDNS.py -b <var1>')
		print('\tEj: python3 gestionDNS.py -b www')

def comprobar_IP(numero_ip,comprobar_red,rango_red):
	if not re.compile('^(\d{1,3}\.){3}(\d{1,3})$').match(numero_ip):
		random_ip=socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
		print('Por favor especifique una IP correcta --> Una IP tiene el formato: "<1-255>.<1-255>.<1-255>.<1-255>"')
		print('\t\tEj: "{}"'.format(random_ip))
		return False
	for num in numero_ip.split('.'):
		if int(num)>255:
			print('Por favor especifique una IP correcta --> Un dígito de la IP no puede ser mayor de "255"')
			return False
	if comprobar_red:
		if not re.compile('^'+rango_red).match(numero_ip):
			ip_final=".".join(map(str, (random.randint(0, 255) for _ in range(2))))
			print('Por favor especifique una IP correcta --> Rango de red: '+rango_red+ip_final)
			return False
	return True

def comprobar_DNS_A(file_dns,nombre):
	with open(file_dns,"r") as fichero:
		for linea in fichero:
			if re.compile('^'+nombre+'.*').match(linea):
				if linea.strip().split()[0]==nombre:
					return True
	return False

def añadir_registroDNS(file_dns,var1,var2,tipo):
	with open(file_dns,'a') as fichero:		
			if tipo=='-dir':
				fichero.write('{}\tIN\tA\t{} ; Añadido con GestionDNS.py\n'.format(var1,var2))
			elif tipo=='-alias':
				fichero.write('{}\tIN\tCNAME\t{} ; Añadido con GestionDNS.py\n'.format(var1,var2))

accion=sys.argv[1]

if accion=='-a':
	if len(sys.argv)!=5:
		mostrar_ayuda(accion)
	else:		
		tipo=sys.argv[2]
		var1=sys.argv[3]
		var2=sys.argv[4]
		if tipo=='-dir' or tipo=='-alias':
			if not os.path.exists(file_dns):
				print("No existe el fichero de resolución Directa")
				sys.exit(0)

			if comprobar_DNS_A(file_dns,var1):
				print('Este registro ya existe')
				sys.exit(0)
			else:
				if tipo=='-dir' and comprobar_IP(var2,comprobar_red,rango_red):
					if not os.path.exists(file_dns_inverso):
						print("No existe el fichero de resolución Inversa")
						sys.exit(0)
					print('Añadir regitro tipo A: \n \t nombre:{} --> IP:{}'.format(var1,var2))
					añadir_registroDNS(file_dns,var1,var2,tipo)
				elif tipo=='-alias':
					print('Añadir regitro tipo CNAME: \n \t alias:{} --> nombre:{}'.format(var1,var2))
					añadir_registroDNS(file_dns,var1,var2,tipo)
		else:
			mostrar_ayuda(accion)
elif accion=='-b':
	if len(sys.argv)!=3:
		mostrar_ayuda(accion)
	else:
		var1=sys.argv[2]
		if not comprobar_DNS_A(file_dns,var1):
			print('Este registro no existe')
			sys.exit(0)
		else:
			print('Borrando registro')
else:
	mostrar_ayuda()