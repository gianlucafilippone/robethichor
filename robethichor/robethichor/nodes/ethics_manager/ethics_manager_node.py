import rclpy
import json
from rclpy.node import Node
from std_msgs.msg import String

from robethichor.nodes.ethics_manager.planner import Planner
from robethichor.nodes.ethics_manager.executor import Executor


class EthicsManagerNode(Node):
    def __init__(self):
        super().__init__('ethics_manager_node')

        # Models initialization
        self.ethic_profiles = dict()
        self.active_profile = dict()

        # Publishers setup
        self.active_profile_publisher = self.create_publisher(String, 'active_profile', 10)

        # Profile update managers initialization
        self.executor_ = Executor(self, self.active_profile, self.ethic_profiles, self.active_profile_publisher)
        self.planner = Planner(self, self.active_profile, self.executor_)

        # Subscribers setup
        self.create_subscription(String, 'ethic_profile', self.ethic_profiles_update_callback, 10)
        self.create_subscription(String, 'current_context', self.planner.plan_active_profile_change, 10)
    

    def ethic_profiles_update_callback(self, msg):
        self.get_logger().info("Called ethic profiles update")
        updated_profile = json.loads(msg.data)
        for label in updated_profile:
            self.ethic_profiles[label] = updated_profile[label]

        # If there is a change in the active profile, refresh it
        if "label" in self.active_profile and self.active_profile["label"] in self.ethic_profiles:
            self.get_logger().info("There is a change in the active profile, refreshing it")
            self.executor_.refresh_active_profile()


def main(args=None):
    rclpy.init(args=args)
    node = EthicsManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()