# Information: https://clover.coex.tech/programming
#
import rospy
from abc import ABC, abstractmethod
from .drone import Drone
from .camera import Camera
from .servo import Servo
from typing import Union
from .files.logger import Logger


class Task(ABC):
    """
    An abstract class to write mission.
    """

    def __init__(self, gpio: Union[int, None] = None) -> None:
        # Initializing task components
        self.drone = Drone()
        self.logger = Logger()
        self.logger.start()
        rospy.sleep(3)

        # Initializig mission report variables 
        self.mission_start_time = rospy.get_rostime().to_sec()
        self.drone_start_battery = self.drone.get_telemetry().voltage 


        if gpio is not None:
            self.servo = Servo(gpio)

        self.camera = Camera()

    def mission_report(self):
        """
        A method to generate a mission report. Useful in most cases.
        """
        rospy.loginfo(f"Mission duration: {self.mission_end_time - self.mission_start_time:.2f} seconds")
        rospy.loginfo(f"Battery used: {self.drone_start_battery - self.drone_end_battery:.2f} V")

    @abstractmethod
    def mission(self) -> None:
        raise Exception("Need implementation.")

    def run(self) -> None:
        """
        A secure method to run a mission. Useful in most cases.
        """

        try:
            rospy.logwarn("Starting task.")
            self.mission()

        except KeyboardInterrupt:
            rospy.logwarn("Aborting task.")
            rospy.sleep(0.5)

        except Exception as e:
            rospy.logerr(e)

        finally:
            self.drone.land_wait()
            self.camera.stop()
            #Mission report variables
            self.mission_end_time = rospy.get_rostime().to_sec()
            self.drone_end_battery = self.drone.get_telemetry().voltage
            self.mission_report()

            rospy.sleep(3)
            self.logger.stop()
