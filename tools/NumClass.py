import numpy as np
##NUMPY CLASS FOR NUMERICAL EXPRESSIONS
##class is set up to overload math operators so that you can do things like Num(3.5) + Num(5.0) or Num(3.0) + 5 or 3 + Num(5.0)
##watch out for divide by zero errors
class Num:
    def __init__(self, op1):
        self.out = np.longdouble(op1)
    def __add__(self, op2):
        if isinstance(op2, Num):
            res = np.add(self.out, op2.out)
            return Num(res)
        else:
            res = np.add(self.out, op2)
            return Num(res)
    def __sub__(self, op2):
        if isinstance(op2, Num):
            res = np.subtract(self.out, op2.out)
            return Num(res)
        else:
            res = np.subtract(self.out, op2)
            return Num(res)
    def __mul__(self, op2):
        if isinstance(op2, Num):
            res = np.multiply(self.out, op2.out)
            return Num(res)
        else:
            res = np.multiply(self.out, op2)
            return Num(res)
    def __truediv__(self, op2):
        if isinstance(op2, Num):
            res = np.divide(self.out, op2.out)
            return Num(res)
        else:
            res = np.divide(self.out, op2)
            return Num(res)
    def __pow__(self, op2):
        if isinstance(op2, Num):
            res = np.power(self.out, op2.out)
            return Num(res)
        else:
            res = np.power(self.out, op2)
            return Num(res)
    def __floordiv__(self, op2):
        if isinstance(op2, Num):
            res = np.floor_divide(self.out, op2.out)
            return Num(res)
        else:
            res = np.floor_divide(self.out, op2)
            return Num(res)
        
    def __mod__(self, op2):
        if isinstance(op2, Num):
            res = np.mod(self.out, op2.out)
            return Num(res)
        else:
            res = np.mod(self.out, op2)
            return Num(res)

    def __lt__(self, op2):
        if isinstance(op2, Num):
            res = np.less(self.out, op2.out)
            return Num(res)
        else:
            res = np.less(self.out, op2)
            return Num(res)
    def __le__(self, op2):
        if isinstance(op2, Num):
            res = np.less_equal(self.out, op2.out)
            return Num(res)
        else:
            res = np.less_equal(self.out, op2)
            return Num(res)
    def __eq__(self, op2):
        if isinstance(op2, Num):
            res = np.equal(self.out, op2.out)
            return Num(res)
        else:
            res = np.equal(self.out, op2)
            return Num(res)
    def __ne__(self, op2):
        if isinstance(op2, Num):
            res = np.not_equal(self.out, op2.out)
            return Num(res)
        else:
            res = np.not_equal(self.out, op2)
            return Num(res)
    def __gt__(self, op2):
        if isinstance(op2, Num):
            res = np.greater(self.out, op2.out)
            return Num(res)
        else:
            res = np.greater(self.out, op2)
            return Num(res)
    def __ge__(self, op2):
        if isinstance(op2, Num):
            res = np.greater_equal(self.out, op2.out)
            return Num(res)
        else:
            res = np.greater_equal(self.out, op2)
            return Num(res)
    def __neg__(self):
        res = np.negative(self.out)
        return Num(res)
    def __abs__(self):
        res = np.absolute(self.out)
        return Num(res)
    def __str__(self):
        return str(self.out)
