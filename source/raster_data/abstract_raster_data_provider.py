import abc

import numpy as np
import threading
import random
import queue


class AbstractRasterDataProvider(abc.ABC):

    def getData(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        assert len(positions_with_zoom.shape) == 2 and positions_with_zoom.shape[0] == 3
        num_chunks = 2048
        cuts = np.linspace(0, positions_with_zoom.shape[1], num_chunks + 1).astype(int)[1:-1]
        parts = np.split(positions_with_zoom, cuts, axis=1)
        assert len(parts) == num_chunks

        thread_results = [None] * num_chunks

        q = queue.Queue()
        queue_data = list(enumerate(parts))
        random.shuffle(queue_data)
        for i, p in queue_data:
            q.put((i, p))

        def _sampleMultithread(qu):
            while True:
                pz = None
                i = None
                try:
                    pair = qu.get(block=False)
                    pz = pair[1]
                    i = pair[0]

                except queue.Empty:
                    return

                r = self._sample(pz)
                thread_results[i] = r

        threads = []
        num_threads = 32
        for tn in range(num_threads):
            t = threading.Thread(target=_sampleMultithread, args=[q])
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
