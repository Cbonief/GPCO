def fun (a,b,c,d):
	print(a)
	print(b)
	print(c)
	print(d)
x = (100,200,300,400)

fun(*x)
y = {'a':'I', 'b':'like','c':'python','d':'programming'}
fun(**y)