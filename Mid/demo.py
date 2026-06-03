import time
import sys
from robot.controller import QuadrupedController
from sim.viewer import Viewer3D


def main():
    robot = QuadrupedController()
    viewer = Viewer3D()

    robot.stand()
    print("=== Standing pose ===")
    robot.print_angles()
    viewer.render(robot)
    viewer.pause(1.0)

    print("\n=== Walking forward (trot) ===")
    robot.set_speed(0.6, 0.0)
    for i in range(60):
        robot.update(1.0)
        viewer.render(robot)
        viewer.pause(0.05)

    print("=== Joint angles during walk ===")
    robot.print_angles()

    print("\n=== Turning ===")
    robot.set_speed(0.4, 0.3)
    for i in range(40):
        robot.update(1.0)
        viewer.render(robot)
        viewer.pause(0.05)

    print("\n=== Slowing down ===")
    robot.set_speed(0.2, 0.0)
    for i in range(30):
        robot.update(1.0)
        viewer.render(robot)
        viewer.pause(0.05)

    print("\n=== Stopping ===")
    robot.set_speed(0.0, 0.0)
    for i in range(10):
        robot.update(1.0)
        viewer.render(robot)
        viewer.pause(0.05)

    robot.stand()
    print("\n=== Final standing pose ===")
    robot.print_angles()

    print("\nPress Ctrl+C or close window to exit.")
    try:
        viewer.show(block=True)
    except KeyboardInterrupt:
        print("Exiting.")


if __name__ == '__main__':
    plt = None
    try:
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure matplotlib is installed: pip install matplotlib")
        sys.exit(1)
