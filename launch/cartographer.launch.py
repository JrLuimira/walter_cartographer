import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.conditions import IfCondition
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time", default="false")
    use_rviz = LaunchConfiguration("use_rviz", default="true")

    # Directories for configuration and resources
    walter_cartographer_prefix = get_package_share_directory("walter_cartographer")
    walter_description_prefix = get_package_share_directory("walter_description")

    cartographer_config_dir = LaunchConfiguration(
        "cartographer_config_dir",
        default=os.path.join(walter_cartographer_prefix, "config"),
    )
    configuration_basename = LaunchConfiguration(
        "configuration_basename",
        default="walter_lds_2d.lua",
        # default="mappers_params_online_async.yaml",
    )

    resolution = LaunchConfiguration("resolution", default="0.05")
    publish_period_sec = LaunchConfiguration("publish_period_sec", default="1.0")

    rviz_config_dir = os.path.join(
        walter_cartographer_prefix, "rviz", "walter_cartographer.rviz"
    )

    # Robot description launch inclusion
    description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(walter_description_prefix, "launch", "gazebo_walter.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "cartographer_config_dir",
                default_value=cartographer_config_dir,
                description="Full path to config file to load",
            ),
            DeclareLaunchArgument(
                "configuration_basename",
                default_value=configuration_basename,
                description="Name of lua file for cartographer",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use simulation (Gazebo) clock if true",
            ),
            # Include the robot description from walter_description
            # description_launch,
            # Cartographer Node
            Node(
                package="cartographer_ros",
                executable="cartographer_node",
                name="cartographer_node",
                output="screen",
                parameters=[{"use_sim_time": use_sim_time}],
                arguments=[
                    "-configuration_directory",
                    cartographer_config_dir,
                    "-configuration_basename",
                    configuration_basename,
                ],
            ),
            DeclareLaunchArgument(
                "resolution",
                default_value=resolution,
                description="Resolution of a grid cell in the published occupancy grid",
            ),
            DeclareLaunchArgument(
                "publish_period_sec",
                default_value=publish_period_sec,
                description="OccupancyGrid publishing period",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        walter_cartographer_prefix, "launch", "occupancy_grid.launch.py"
                    )
                ),
                launch_arguments={
                    "use_sim_time": use_sim_time,
                    "resolution": resolution,
                    "publish_period_sec": publish_period_sec,
                }.items(),
            ),
            # RViz Node
            # Node(
            #      package="rviz2",
            #      executable="rviz2",
            #      name="rviz2",
            #      arguments=["-d", rviz_config_dir],
            #      parameters=[{"use_sim_time": use_sim_time}],
            #      condition=IfCondition(use_rviz),
            #      output="screen",
            #  ),
        ]
    )
