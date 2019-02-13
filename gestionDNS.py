import subprocess, sys, re
# para generacioń de IPs aleatorias
import random, socket, struct
# para verificar que existe fichero
import os.path

file_dns='/var/cache/bind/ext-juanpe.gonzalonazareno.org'
file_dns_inverso='/var/cache/bind/ext-200.22.172.in-addr.arpa'
#file_dns='prueba-ext'
#file_dns_inverso='prueba-inv'

## Para el caso de gestionar el DNS interno
#file_dns_int='/var/cache/bind/int-juanpe.gonzalonazareno.org'
#file_dns_inverso_int='/var/cache/bind/int-10.in-addr.arpa'

## Para comprobar que sea del mismo rango de ip *1
comprobar_red=True
rango_red='172.22.200.'
##

## Nombre de dominio
dominio='juanpe.gonzalonazareno.org.'
##

## Mostrar ayuda
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
##

## Comprobar sintaxis de IP y rango de red si se habilita[1]
def comprobar_IP(numero_ip,comprobar_red,rango_red):
	if not re.compile('^(\d{1,3}\.){3}(\d{1,3})$').match(numero_ip):
		random_ip=socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
		print('Por favor especifique una IP correcta --> Una IP tiene el formato: "<1-255>.<1-255>.<1-255>.<1-255>".')
		print('\t\tEj: "{}"'.format(random_ip))
		return False
	for num in numero_ip.split('.'):
		if int(num)>255:
			print('Por favor especifique una IP correcta --> Un dígito de la IP no puede ser mayor de "255".')
			return False
	if comprobar_red:
		if not re.compile('^'+rango_red).match(numero_ip):
			ip_final=".".join(map(str, (random.randint(0, 255) for _ in range(1))))
			print('Por favor especifique una IP correcta --> Rango de red: '+rango_red+ip_final)
			return False
	return True
##

## Comprobar si existe un registro con el "nombre" dado.
def comprobar_DNS_A(file_dns,nombre,tipo=None):
	with open(file_dns,"r") as fichero:
		for linea in fichero:			
			parametros=' '.join(linea.split()).replace(' ',':').split(':')
			if tipo!=None:
				if parametros[0]==nombre and parametros[1]=='IN' and parametros[2]=='A':
					return True
			else:
				if parametros[0]==nombre:
					return True
	return False
##

## Añadimos registro. En tipo de resgistro CNAME compruba si existe un registro A para asignar como alias.
## En tipo A añade regitro inverso.
def añadir_registroDNS(file_dns,file_dns_inverso,var1,var2,tipo,dominio=None):			
	if tipo=='-dir':
		print('Añadir regitro tipo A:\n\t"{}\t\tIN\tA\t{}"'.format(var1,var2))
		linea='{}\t\tIN\tA\t{} ; Añadido con GestionDNS.py\n'.format(var1,var2)
		ip_var2=var2.split('.')[3]
		linea_inversa='{}\tIN\tPTR\t{}.{} ; Añadido con GestionDNS.py\n'.format(ip_var2,var1,dominio)
		escribir_zonadirecta=True
	elif tipo=='-alias':
		if comprobar_DNS_A(file_dns,var2,tipo):
			print('Añadir regitro tipo CNAME:\n\t"{}\t\tIN\tCNAME\t{}"'.format(var1,var2))
			linea='{}\t\tIN\tCNAME\t{} ; Añadido con GestionDNS.py\n'.format(var1,var2)
			escribir_zonadirecta=True
		else:
			escribir_zonadirecta=False
			print('No existe un registro A "{}" para asociar este resgistro CNAME "{}".'.format(var2,var1))
	if escribir_zonadirecta:
		with open(file_dns,'a') as fichero:
			fichero.write(linea)
		subprocess.call(['rndc','reload'])
	if dominio!=None:
		print('Añadir regitro tipo PTR: \n \t IP: "{}" --> nombre: "{}.{}"'.format(var2,var1,dominio))
		with open(file_dns_inverso,'a') as fichero:
			fichero.write(linea_inversa)
		subprocess.call(['rndc','reload'])
##

## Eliminar registros
def eliminar_registroDNS(file_dns,file_dns_inverso,var1,dominio):
	eliminar_inverso=False
	## Eliminar entrada en dona directa
	fichero = open(file_dns,'r')
	lineas = fichero.readlines()
	fichero.close()
	fichero = open(file_dns,'w')
	for linea in lineas:
		parametros=' '.join(linea.split()).replace(' ',':').split(':')
		if parametros[0]!=var1:
			fichero.write(linea)
		else:
			print('Borrando registro "{}\tIN\t{}\t{}.{}" en zona directa.'.format(parametros[0],parametros[2],parametros[3],parametros[4]))
			if parametros[2]=='A':
				eliminar_inverso=True
	fichero.close()
	subprocess.call(['rndc','reload'])
	## Eliminar entrada en zona inversa si es registro tipo A
	if eliminar_inverso:
		fichero = open(file_dns_inverso,'r')
		lineas = fichero.readlines()
		fichero.close()
		fichero = open(file_dns_inverso,'w')
		for linea in lineas:
			parametros=' '.join(linea.split()).replace(' ',':').split(':')
			if len(parametros)>3 and parametros[3]==var1+'.'+dominio:
				print('Borrando registro "{}\tIN\tPTR\t{}" en zona inversa.'.format(parametros[0],parametros[3]))
			else:
				fichero.write(linea)				
		fichero.close()
		subprocess.call(['rndc','reload'])
##

## accion debe ser o "-a" o "-b"
accion=sys.argv[1]
##

## programa principal
if accion=='-a':
	if len(sys.argv)!=5:
		mostrar_ayuda(accion)
	else:		
		tipo=sys.argv[2]
		var1=sys.argv[3]
		var2=sys.argv[4]
		if tipo=='-dir' or tipo=='-alias':
			if not os.path.exists(file_dns):
				print("No existe el fichero de resolución Directa.")
				sys.exit(0)

			if comprobar_DNS_A(file_dns,var1):
				print('El registro con nombre "{}" ya existe'.format(var1))
				sys.exit(0)
			else:
				if tipo=='-dir' and comprobar_IP(var2,comprobar_red,rango_red):
					if not os.path.exists(file_dns_inverso):
						print("No existe el fichero de resolución Inversa.")
						sys.exit(0)
					else:
						añadir_registroDNS(file_dns,file_dns_inverso,var1,var2,tipo,dominio)
				elif tipo=='-alias':					
					añadir_registroDNS(file_dns,file_dns_inverso,var1,var2,tipo)
		else:
			mostrar_ayuda(accion)
elif accion=='-b':
	if len(sys.argv)!=3:
		mostrar_ayuda(accion)
	else:
		var1=sys.argv[2]
		if not comprobar_DNS_A(file_dns,var1):
			print('El registro con nombre "{}" no existe.'.format(var1))
			sys.exit(0)
		else:
			eliminar_registroDNS(file_dns,file_dns_inverso,var1,dominio)
else:
	mostrar_ayuda()
##