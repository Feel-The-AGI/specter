import spaces

from specter_controller.space import demo


@spaces.GPU
def zerogpu_placeholder() -> None:
    return None


demo.launch()
