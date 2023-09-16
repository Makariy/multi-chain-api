from typing import Optional
import time


def rps_limit_middleware(rps_limit: float = 1., sleep_time: float = 0.1):
    last_request_time: Optional[float] = None

    def _request_limit_middleware_wrapper(make_request, w3):
        def middleware(method, params):
            nonlocal last_request_time

            # Wait for rps_limit
            while True:
                if not last_request_time:
                    break
                if time.time() > last_request_time + 1 / rps_limit:
                    break
                time.sleep(sleep_time)

            response = make_request(method, params)
            last_request_time = time.time()
            return response

        return middleware
    return _request_limit_middleware_wrapper


