from launch import LaunchDescription
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument, RegisterEventHandler

import os
import xacro
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    package_name = 'tb3_hw_interface'
    package_share = FindPackageShare(package=package_name).find(package_name)

    urdf_filename = 'tb3_hw.urdf.xacro'

    use_rsp = LaunchConfiguration('use_rsp')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config_path = LaunchConfiguration('rviz_config_path')
    use_lidar = LaunchConfiguration('use_lidar')
    lidar_frame_id = LaunchConfiguration('lidar_frame_id')

    declare_use_rsp = DeclareLaunchArgument(
        name='use_rsp',
        default_value='true',
        description='Whether to launch robot state publisher'
    )

    declare_use_rviz = DeclareLaunchArgument(
        name='use_rviz',
        default_value='false',
        description='Whether to start RViz'
    )
    
    declare_rviz_config_path = DeclareLaunchArgument(
        name='rviz_config_path',
        default_value=os.path.join(package_share, 'config', 'rviz_config.rviz'),
        description='Location of RViz config file'
    )

    declare_use_lidar = DeclareLaunchArgument(
        name='use_lidar',
        default_value='true',
        description='Whether to launch lidar driver'
    )

    declare_lidar_frame_id = DeclareLaunchArgument(
        name='lidar_frame_id',
        default_value='base_scan',
        description='Frame id for LazerScan messages'
    )

    urdf_path = os.path.join(package_share, 'urdf', urdf_filename)
    robot_description = xacro.process_file(urdf_path).toxml()
    robot_state_publisher = Node(
        condition=IfCondition(use_rsp),
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )
    
    robot_controllers = os.path.join(package_share, "config", "controllers.yaml")
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controllers],
        output="screen",
        remappings=[('/tb3_base_controller/odom', '/odom')],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "tb3_base_controller",
            "--param-file",
            robot_controllers,
        ],
    )

    twist_stamper = Node(
        package='twist_stamper',
        executable='twist_stamper',
        remappings=[
            ('/cmd_vel_in','/cmd_vel_out'),
            ('/cmd_vel_out','/tb3_base_controller/cmd_vel')
        ]
    )

    lidar_manager = Node(
        condition=IfCondition(use_lidar),
        package='rplidar_ros',
        executable='rplidar_composition',
        output='screen',
        parameters=[{
            'serial_port': '/dev/ttyUSB0',
            'serial_baudrate': 115200,
            'frame_id': lidar_frame_id,
            'inverted': False,
            'angle_compensate': True,
        }],
    )

    rviz = Node(
        condition=IfCondition(use_rviz),
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )

    ld = LaunchDescription()

    ld.add_action(declare_use_rsp)
    ld.add_action(declare_use_rviz)
    ld.add_action(declare_rviz_config_path)
    ld.add_action(declare_use_lidar)
    ld.add_action(declare_lidar_frame_id)

    ld.add_action(controller_manager)
    ld.add_action(robot_state_publisher)
    ld.add_action(joint_state_broadcaster_spawner)
    ld.add_action(robot_controller_spawner)
    ld.add_action(twist_stamper)
    ld.add_action(lidar_manager)
    ld.add_action(rviz)

    return ld