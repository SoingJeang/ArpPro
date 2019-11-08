#加密

#https://scapy.net/

key='A'							  #密钥
message='haoiphgaop'			  #明文
ml=len(message)					  #分别得到密钥和明文的长度
kl=len(key)
key=ml//kl*key+key[:ml%kl]		  #因为要一对一的异或，所以key要变化
pwd=[]						      #通过取整，求余的方法重新得到key
for i in range(len(key)):
	pwd.append(chr(ord(key[i])^ord(message[i]))) #一对一异或操作，得到结果,其中,"ord(char)"得到该字符对应的ASCII码,"chr(int)"刚好相反
print(''.join(pwd))


#解密
result=[]
#pwd为密文
for j in range(len(key)):
    result.append(chr(ord(pwd[j])^ord(key[j]))) #跟KEY异或回去就是原明文
result=''.join(result)
print(result)

def encrypy():
    pass

def decrypt():
    pass