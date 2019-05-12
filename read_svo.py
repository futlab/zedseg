from multiprocessing import Process, Queue
from queue import Empty
import pyzed.sl as sl


def process(q: Queue, fn: str):
    runtime = sl.RuntimeParameters()
    mat = sl.Mat()
    init = sl.InitParameters(svo_input_filename=fn, svo_real_time_mode=False)
    cam = sl.Camera()
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()
    while True:
        err = cam.grab(runtime)
        if err == sl.ERROR_CODE.ERROR_CODE_NOT_A_NEW_FRAME:
            break
        assert err == sl.ERROR_CODE.SUCCESS
        cam.retrieve_image(mat)
        data = mat.get_data()[..., :3]  # [200:520, 400:720]
        q.put(data)
    cam.close()


def read_svo(file_name):
    q = Queue()
    p = Process(target=process, args=(q, file_name))
    p.start()
    while p.is_alive():
        try:
            image = q.get(block=True, timeout=0.1)
            yield image
        except Empty:
            pass
    p.join()