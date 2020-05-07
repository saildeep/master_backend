from typing import Callable

import numpy as np




def _vectorsComplexWrapper(vecIn:np.ndarray,fn:Callable[[np.ndarray],np.ndarray])->np.ndarray:


    assert vecIn.shape[0] == 2 and len(vecIn.shape) == 2
    x = vecIn[0, :]
    y = vecIn[1, :]
    fn_out = fn(x + 1j * y)
    x = np.real(fn_out)
    x[x == -np.inf] = 0 # replace negative infinity with 0 hack
    y = np.imag(fn_out)
    out = np.stack([x, y], axis=0)



    assert out.shape == vecIn.shape
    return out


# input 2xX area
def complexLog(vecIn:np.ndarray)->np.ndarray:
    return _vectorsComplexWrapper(vecIn,np.log)

def complexExp(vecIn:np.ndarray)->np.ndarray:
    return _vectorsComplexWrapper(vecIn,np.exp)