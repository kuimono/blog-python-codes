"""
This file serves as example on how to wrap a separate process in a async IO function.
"""
import asyncio
import logging
from multiprocessing import Process, Queue
from queue import Empty
from typing import Optional

sleep_interval = 1


async def run_process(*args):
    send_queue = Queue()
    receive_queue = Queue()

    if args:
        args = (*args, send_queue, receive_queue)
    else:
        args = (send_queue, receive_queue)

    process = Process(target=blocking_process_func, args=args)
    process.start()

    result_value = None
    while True:
        # get all msg from the receive_queue
        while True:
            msg_received = _try_get(receive_queue)
            if msg_received:
                result_value = await _handle_msg_received(msg_received)
                if result_value:
                    break
            else:
                break

        if process.is_alive():
            await asyncio.sleep(sleep_interval)
        else:
            break

    # clean up
    process.join()
    send_queue.close()
    receive_queue.close()

    return result_value


async def _handle_msg_received(msg) -> Optional[str]:
    """
    Handler of the message received from the blocking process.
    This is just an illustration, without actually calling any async IO operations.
    """
    msg_type, args = msg
    if msg_type == "PROGRESS":
        logging.debug(f"Update progress: {args}")
        logging.debug(f"call some async function to update the DB....")
    if msg_type == "COMPLETED":
        logging.debug(f"Process completed")
        logging.debug(f"result size: {len(args.get('result'))}")
        logging.debug("cal some async function to store the result file...")
        return "some result value"


def blocking_process_func(*args):
    """
    The logic of the blocking process.
    """
    logging.debug(f"Running blocking_process_func with args {args}")
    *args, receive_queue, send_queue = args

    # The following code is just a dummy of a "blocking process".
    # using a loop is just to illustrate what can it do with the send_queue and receive_queue.
    iterations = 10
    for i in range(iterations):
        msg_received = _try_get(receive_queue)
        if msg_received:
            logging.debug("blocking_process_func: msg received")
            logging.debug("do something related to the received msg")

        logging.debug(f"iteration {i+1}: do the work...")
        send_queue.put(("PROGRESS", {"finished": i + 1, "total": iterations}))

    send_queue.put(("COMPLETED", {"result": b"process result e.g. binary of the result AI model"}))


def _try_get(queue: Queue):
    msg = None
    try:
        msg = queue.get_nowait()
    except Empty:
        pass

    return msg
