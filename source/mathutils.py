import numpy as np
import math


def _vectorsComplexWrapper(vecIn: np.ndarray, fn: np.ufunc) -> np.ndarray:
    assertMultipleVec2d(vecIn)
    x = vecIn[0, :]
    y = vecIn[1, :]
    fn_out = fn(x + 1j * y)
    x = np.real(fn_out)
    x[x == -np.inf] = 0  # replace negative infinity with 0 hack
    y = np.imag(fn_out)
    out = np.stack([x, y], axis=0)
    assert out.shape == vecIn.shape
    return out


def assertMultipleVec2d(vec: np.ndarray) -> np.ndarray:
    assert vec.shape[0] == 2 and len(vec.shape) == 2
    return vec


def assertSingleVec2d(vec: np.ndarray) -> np.ndarray:
    assertMultipleVec2d(vec)
    assert vec.shape[1] == 1
    return vec


# input 2xX area
def complexLog(vecIn: np.ndarray) -> np.ndarray:
    return _vectorsComplexWrapper(vecIn, np.log)


def complexExp(vecIn: np.ndarray) -> np.ndarray:
    return _vectorsComplexWrapper(vecIn, np.exp)


def midpoint(*points: np.ndarray) -> np.ndarray:
    for p in points:
        assertSingleVec2d(p)
    stacked = np.concatenate(points, axis=1)
    mean = np.mean(stacked, axis=1, keepdims=True)
    return assertSingleVec2d(mean)


def vectorAngles(vec: np.ndarray) -> np.ndarray:
    assertMultipleVec2d(vec)
    res = np.arctan2(vec[1, :], vec[0, :])
    res[res >= math.pi] -= 2 * math.pi
    return res


def euclideanDistSquared(points: np.ndarray, point: np.ndarray) -> np.ndarray:
    assertMultipleVec2d(point)
    assertMultipleVec2d(points)
    res = np.sum(np.square(points - point), axis=0)
    return res


def euclideanDist(points: np.ndarray, point: np.ndarray) -> np.ndarray:
    return np.sqrt(euclideanDistSquared(points, point))


def createRotationMatrix(angle: float) -> np.ndarray:
    return np.array([
        [math.cos(angle), -1 * math.sin(angle)],
        [math.sin(angle), math.cos(angle)
         ]
    ])


# map any angle to -pi to pi range
def normalizeAngles(angles: np.ndarray) -> np.ndarray:
    angles = np.remainder(angles, 2 * math.pi)
    selection = angles > math.pi
    angles[selection] -= 2 * math.pi
    return angles

def anglesBetween(vecs1:np.ndarray,vecs2:np.ndarray):
    assertMultipleVec2d(vecs1)
    assertMultipleVec2d(vecs2)
    assert vecs1.shape[1] == vecs2.shape[1] or vecs1.shape[1] ==1 or vecs2.shape[1]

    return np.arccos(np.sum(vecs1 * vecs2,axis=0,keepdims=True))
