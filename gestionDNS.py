import subprocess, sys

file_dns='/var/cache/bind/ext-juanpe.gonzalonazareno.org'
file_dns_inverso='/var/cache/bind/ext-200.22.172.in-addr.arpa'

#file_dns_int='/var/cache/bind/int-juanpe.gonzalonazareno.org'
#file_dns_inverso_int='/var/cache/bind/int-10.in-addr.arpa'

def mostrar_ayuda(accion=None,tipo=None):	
	if accion=='-a':
		if tipo!=None:
			print('Uso -a: Añade un registro en el DNS')
			print('\t Ej: python3 gestionDNS.py -a < -dir | -alias > <var1>  <var2>')

		if tipo=='-dir':
			print('\t -dir: Añade un registro tipo A con nombre igual a <var1> e IP igual a <var2>')
		elif tipo=='-alias':
			print('\t -alias: Añade un registro tipo CNAME con nombre igual a <var1> asociado al registro A <var2>')
		elif tipo==None:
			mostrar_ayuda('-a','-dir')
			mostrar_ayuda('-a','-alias')

	elif accion=='-b':
		print('Uso -b: Borra un registro en el DNS')
		print('\t Ej: python3 gestionDNS.py -b <var1>')
	elif accion==None:
		mostrar_ayuda('-a')
		print('')
		mostrar_ayuda('-b')






accion=sys.argv[1]

if accion=='-a':
	if len(sys.argv)!=5:
		mostrar_ayuda(accion)
	else:		
		tipo=sys.argv[2]
		if tipo=='-dir':
			print('Añadir regitro tipo A: \n \t nombre:{} --> IP:{}'.format(sys.argv[3],sys.argv[4]))
		elif tipo=='-alias':
			print('Añadir regitro tipo CNAME: \n \t alias:{} --> nombre:{}'.format(sys.argv[3],sys.argv[4]))
		else:
			mostrar_ayuda(accion,tipo)
elif accion=='-b':
	if len(sys.argv)!=3:
		mostrar_ayuda(accion)
	else:
		print('Borrando registro')
else:
	mostrar_ayuda()