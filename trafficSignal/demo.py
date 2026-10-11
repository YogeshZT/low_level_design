import threading
import time
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from enum import Enum


class Status(Enum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"


class Mode(Enum):
    STANDARD = "standard"
    EMERGENCY = "emergency"


class LightConfig:
    def __init__(self, green_duration : int, yellow_duration : int):
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration

    def get_green_duration(self) -> int:
        return self.green_duration

    def get_yellow_duration(self) -> int:
        return self.yellow_duration


class Clock:
    def __init__(self):
        self.start_time : float = time.time()

    def get_elapsed_time(self) -> float:
        return time.time() - self.start_time

    def is_duration_complete(self, duration : float) -> bool:
        return duration <= self.get_elapsed_time()

    def reset(self):
        self.start_time = time.time()


class TrafficLight:
    def __init__(self, id: int, config : LightConfig):
        self.id = id
        self.config = config
        self.clock : Clock = Clock()
        self.status : Status = Status.RED

    def set_config(self, new_config : LightConfig):
        self.config = new_config

    def get_config(self) -> LightConfig:
        return self.config

    def get_status(self) -> Status:
        return self.status

    def change_status(self, new_status : Status):
        self.status = new_status
        self.clock.reset()
        print(f"[Light {self.get_id()}] status changed to {self.status.value.upper()} at {time.strftime('%X')}")

    def get_id(self) -> int:
        return self.id

    def is_duration_complete(self) -> bool:
        return self.clock.is_duration_complete(self.config.green_duration if self.status == Status.GREEN else self.config.yellow_duration)


class TrafficController:
    def __init__(self, lights : list[TrafficLight]):
        self.lights = lights
        self.current_light_id = 0

        self.light_id_map : dict[int, TrafficLight] = defaultdict(None)

        for light in lights:
            self.light_id_map[light.get_id()] = light

        self._lock = threading.Lock()
        self.executor : ThreadPoolExecutor | None = None

        self._is_running : bool = False

    def set_current_light_id(self, new_id : int):
        self.current_light_id = new_id

    def get_current_light_id(self) -> int:
        return self.current_light_id

    def get_lights(self) -> list[TrafficLight]:
        return self.lights

    def step(self):
        current_light = self.light_id_map[self.get_current_light_id()]

        if current_light.is_duration_complete():
            if current_light.get_status() == Status.GREEN:
                current_light.change_status(Status.YELLOW)

            elif current_light.get_status() == Status.RED:
                current_light.change_status(Status.GREEN)

            else :
                current_light.change_status(Status.RED)
                next_light_id = (current_light.get_id() + 1) % len(self.get_lights())

                next_light = self.light_id_map[next_light_id]
                next_light.change_status(Status.GREEN)
                self.set_current_light_id(next_light_id)


    def run_light(self, light : TrafficLight):
        while self._is_running:
            with self._lock:
                if light.get_id() == self.light_id_map[self.current_light_id].get_id():
                    self.step()

            time.sleep(0.1)


    def start(self):
        if self._is_running:
            return

        self._is_running = True

        for light in self.lights:
            if light.get_id() == self.get_current_light_id():
                light.change_status(Status.GREEN)
            else:
                light.change_status(Status.RED)

        self.executor = ThreadPoolExecutor(max_workers=len(self.lights))
        for light in self.lights:
            self.executor.submit(self.run_light, light)


    def stop(self):
        if self._is_running:
            self._is_running = False
            self.executor.shutdown(wait=True)


if __name__ == "__main__":
    light_config = LightConfig(green_duration=2, yellow_duration=1)
    light0=TrafficLight(0, light_config)
    light1 = TrafficLight(1, light_config)
    light2 = TrafficLight(2, light_config)
    light3 = TrafficLight(3, light_config)

    traffic_controller = TrafficController([light0, light1, light2, light3])

    print("starting the traffic controller on the main thread...")
    traffic_controller.start()

    try :
        time.sleep(100)
    finally:
        print("stopping the traffic controller system...")
        traffic_controller.stop()