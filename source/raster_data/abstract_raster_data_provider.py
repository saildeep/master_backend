import abc
import numpy as np
import threading


class AbstractRasterDataProvider(abc.ABC):

    def getData(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        assert len(positions_with_zoom.shape) == 2 and positions_with_zoom.shape[0] == 3
        num_threads = 8
        cuts = np.linspace(0, positions_with_zoom.shape[1], num_threads + 1).astype(int)[1:-1]
        parts = np.split(positions_with_zoom, cuts, axis=1)
        assert len(parts) == num_threads

        thread_results = [None] * num_threads

        def _sampleMultithread(positions_with_zoom: np.ndarray, index: int):
            r = self._sample(positions_with_zoom)
            thread_results[index] = r

        threads = []
        for i, part in enumerate(parts):
            t = threading.Thread(target=_sampleMultithread, args=[part, i])
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        res = np.concatenate(thread_results, axis=1)

        # res = self._sample(positions_with_zoom)
        assert res.shape == positions_with_zoom.shape
        assert res.dtype == np.uint8

        return res

    @abc.abstractmethod
    # gets x,y, zoomlevel and should equally sized RGB
    def _sample(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        pass
