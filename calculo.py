potency = 1000 #1kw

Np = 1
Ns = 2000

aref = 3.3

voltage = int(input("que voltaje se esta usando?"))

Irms = potency/voltage

Ipico = Irms * (2**(1/2)) 


Ipicons = Np*Ipico/Ns

Rcarga = (aref/2)/Ipicons

print("Irms =" + str(Irms) + "\n"
 + "Ipico =" + str(Ipico) + "\n" + 
 "Ipicons =" + str(Ipicons) + "\n" )

print(Rcarga)