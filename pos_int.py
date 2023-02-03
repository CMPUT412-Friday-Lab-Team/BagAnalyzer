import rosbag
import cv2
import numpy as np
import math
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
import cv_plot
import wheel_int


HOSTNAME = "csc22926"


bag = rosbag.Bag('data.bag')

output_files = {}

TIME_CUTOFF_MIN = 1675459850
TIME_CUTOFF_MAX = 1675459885
SILENCED_TOPICS = (f'/{HOSTNAME}/camera_node/image/compressed', 
                   f'/{HOSTNAME}/display_driver_node/fragments', 
                   f'/{HOSTNAME}/camera_node/camera_info',
                   f'/{HOSTNAME}/diagnostics/ros/links',
                   '/diagnostics',
                   #f'/{HOSTNAME}/diagnostics/ros/topics',
                   # f'/{HOSTNAME}/front_center_tof_driver_node/range',
                   # f'/{HOSTNAME}/diagnostics/code/profiling',
                   '/my_publisher_node/diagnostics/ros/topics',
                   '/my_publisher_node/diagnostics/ros/links',
                   # f'/{HOSTNAME}/wheels_driver_node/wheels_cmd',
                   # f'/{HOSTNAME}/wheels_driver_node/wheels_cmd_executed',
                   '/rosout_agg')

x, y, theta, time = 0.0, 0.0, 0.0, None

xList, yList = [], []
int_wheel = wheel_int.WheelPositionIntegration(40)
int_wheel_state = int_wheel.get_state()
fig, ax = plt.subplots(1, 1)
i = 0
ax.set_xlim(-1000, 1250)
ax.set_ylim(-1000, 1250)
ax.set_aspect('equal', adjustable='box')

for topic, msg, t in bag.read_messages(topics=[f'/{HOSTNAME}/kinematics_node/velocity', f'/{HOSTNAME}/camera_node/image/compressed', 
                                               f'/{HOSTNAME}/left_wheel_encoder_node/tick', f'/{HOSTNAME}/right_wheel_encoder_node/tick', 
                                               f'/{HOSTNAME}/wheels_driver_node/wheels_cmd_executed']):
    if t.secs < TIME_CUTOFF_MIN:
        continue
    elif t.secs > TIME_CUTOFF_MAX:
        break

    if topic == f'/{HOSTNAME}/camera_node/image/compressed':
        key = cv2.waitKey(250)
        if key == 27:
            break

        compressed_image = np.frombuffer(msg.data, np.uint8)
        im = cv2.imdecode(compressed_image, cv2.IMREAD_COLOR)
        cv2.imshow('test', im)
    elif topic == f'/{HOSTNAME}/left_wheel_encoder_node/tick':
        int_wheel.update_left(msg.data, t)
        x, y, theta = int_wheel_state
        int_wheel_state = int_wheel.get_state()
        newx, newy, newtheta = int_wheel_state
        cv_plot.plot_path(ax, (x, newx), (y, newy))
        i += 1
        if i % 20 == 0:
            cv_plot.cv_show_plot(fig)
        print(f'left tick:{msg.data}')
        print(f'cur state: x_{x: .3f} y_{y: .3f} theta_{theta: .3f} t_{t.nsecs * 1e-9 + t.secs: .3f}')
    elif topic == f'/{HOSTNAME}/right_wheel_encoder_node/tick':
        int_wheel.update_right(msg.data, t)
        x, y, theta = int_wheel_state
        int_wheel_state = int_wheel.get_state()
        newx, newy, newtheta = int_wheel_state
        cv_plot.plot_path(ax, (x, newx), (y, newy))
        i += 1
        if i % 20 == 0:
            cv_plot.cv_show_plot(fig)
        print(f'right tick:{msg.data}')
        print(f'cur state: x_{x: .3f} y_{y: .3f} theta_{theta: .3f} t_{t.nsecs * 1e-9 + t.secs: .3f}')
    elif topic == f'/{HOSTNAME}/wheels_driver_node/wheels_cmd_executed':
        print(msg.vel_left, msg.vel_right)
        


bag.close()

for file in output_files.values():
    file.close()